from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import HttpRequest
from django.middleware.csrf import get_token
from ninja import Router
from ninja.errors import HttpError
from ninja.utils import check_csrf

from accounts.models import User
from accounts.schemas import Detail, LoginIn, RegisterIn, UserOut

router = Router(tags=["auth"])


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
