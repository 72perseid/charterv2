from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpRequest
from django.middleware.csrf import get_token
from ninja import Router
from ninja.errors import HttpError
from ninja.utils import check_csrf

from accounts.crypto import decrypt, encrypt
from accounts.models import ModelConfig, User
from accounts.schemas import (
    Detail,
    LoginIn,
    ModelConfigIn,
    ModelConfigOut,
    ModelListIn,
    ModelListOut,
    ModelTestOut,
    RegisterIn,
    UserOut,
)
from generation.provider import ProviderError, chat_completion, list_models, normalise_base_url

router = Router(tags=["auth"])
me_router = Router(tags=["me"])


def require_csrf(request: HttpRequest) -> None:
    """Session-authenticated routes get this check from django_auth; the two
    routes that run before a session exists (register, login) call it themselves."""
    if check_csrf(request) is not None:
        raise HttpError(403, "CSRF check failed")


@router.get("/csrf", auth=None, response={204: None})
def csrf(request: HttpRequest):
    """Sets the csrftoken cookie. The frontend calls this once before any POST."""
    get_token(request)
    return 204, None


@router.post("/register", auth=None, response={201: UserOut, 400: Detail, 409: Detail})
def register(request: HttpRequest, data: RegisterIn):
    require_csrf(request)
    try:
        validate_password(data.password)
    except ValidationError as exc:
        return 400, {"detail": " ".join(exc.messages)}
    try:
        user = User.objects.create_user(
            email=data.email, password=data.password, display_name=data.display_name
        )
    except IntegrityError:
        return 409, {"detail": "An account with this email already exists."}
    login(request, user)
    return 201, user


@router.post("/login", auth=None, response={200: UserOut, 401: Detail})
def login_view(request: HttpRequest, data: LoginIn):
    require_csrf(request)
    user = authenticate(request, username=data.email, password=data.password)
    if user is None:
        return 401, {"detail": "Email or password is incorrect."}
    login(request, user)
    return 200, user


@router.post("/logout", response={204: None})
def logout_view(request: HttpRequest):
    logout(request)
    return 204, None


@router.get("/me", response={200: UserOut, 401: Detail})
def me(request: HttpRequest):
    get_token(request)
    return 200, request.user


# --- bring-your-own-key model configuration (SPEC §7, /me/model-config) ------

TEST_MAX_TOKENS = 1024

EMPTY_CONFIG = {
    "base_url": "",
    "model": "",
    "temperature": 0.0,
    "has_key": False,
    "key_hint": "",
    "input_price_per_million": None,
    "output_price_per_million": None,
    "updated_at": None,
}


def config_out(config: ModelConfig) -> dict:
    key = decrypt(config.api_key_encrypted)
    return {
        "base_url": config.base_url,
        "model": config.model,
        "temperature": config.temperature,
        "has_key": True,
        "key_hint": ("…" + key[-4:]) if len(key) >= 8 else "…",
        "input_price_per_million": config.input_price_per_million,
        "output_price_per_million": config.output_price_per_million,
        "updated_at": config.updated_at,
    }


@me_router.get("/model-config", response=ModelConfigOut)
def get_model_config(request: HttpRequest):
    config = ModelConfig.objects.filter(user=request.user).first()
    return config_out(config) if config else EMPTY_CONFIG


@me_router.put("/model-config", response={200: ModelConfigOut, 400: Detail})
def put_model_config(request: HttpRequest, data: ModelConfigIn):
    try:
        base_url = normalise_base_url(data.base_url)
    except ProviderError as exc:
        return 400, {"detail": str(exc)}
    config = ModelConfig.objects.filter(user=request.user).first()
    api_key = data.api_key.strip()
    if not api_key:
        if config is None:
            return 400, {"detail": "An API key is required."}
        encrypted = bytes(config.api_key_encrypted)
    else:
        encrypted = encrypt(api_key)
    config, _ = ModelConfig.objects.update_or_create(
        user=request.user,
        defaults={
            "base_url": base_url,
            "model": data.model.strip(),
            "temperature": data.temperature,
            "input_price_per_million": data.input_price_per_million,
            "output_price_per_million": data.output_price_per_million,
            "api_key_encrypted": encrypted,
        },
    )
    return 200, config_out(config)


@me_router.post("/model-config/test", response={200: ModelTestOut, 400: Detail})
def test_model_config(request: HttpRequest):
    """One tiny call with the stored settings. Reports what happened (SPEC §7)."""
    config = ModelConfig.objects.filter(user=request.user).first()
    if config is None:
        return 400, {"detail": "Save a model configuration first."}
    try:
        result = chat_completion(
            base_url=config.base_url,
            api_key=decrypt(config.api_key_encrypted),
            model=config.model,
            messages=[{"role": "user", "content": "Reply with the single word: ok"}],
            temperature=0.0,
            # Reasoning models spend hidden tokens before the first visible word,
            # so the cap has to leave room for that. The prompt keeps the answer short.
            max_tokens=TEST_MAX_TOKENS,
            timeout=60,
        )
    except ProviderError as exc:
        return 200, {"ok": False, "message": str(exc)}
    except ValueError as exc:
        return 200, {"ok": False, "message": str(exc)}
    message = f"Connected. The model answered: {result.text.strip()[:40]!r}"
    if result.adjustments:
        message += " Adjusted for this endpoint: " + ", ".join(result.adjustments) + "."
    return 200, {
        "ok": True,
        "message": message,
        "model": result.model,
        "duration_ms": result.duration_ms,
    }


@me_router.post("/model-config/models", response={200: ModelListOut, 400: Detail})
def list_provider_models(request: HttpRequest, data: ModelListIn):
    """Ask the provider at base_url for its model list, so the user picks a
    real name instead of guessing one. Uses the pasted key, or the stored one."""
    api_key = data.api_key.strip()
    if not api_key:
        config = ModelConfig.objects.filter(user=request.user).first()
        if config is None:
            return 400, {"detail": "Enter an API key first."}
        api_key = decrypt(config.api_key_encrypted)
    try:
        listed = list_models(base_url=data.base_url, api_key=api_key)
        return 200, {"models": listed.ids, "pricing": listed.pricing}
    except ProviderError as exc:
        return 400, {"detail": str(exc)}
