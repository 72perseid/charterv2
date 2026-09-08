"""
Chart-er settings. Everything environment-specific comes from the process
environment; see deploy/.env.example for the full list.
"""

import os
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).resolve().parent.parent


def env(name: str, default: str | None = None) -> str:
    value = os.environ.get(name, default)
    if value is None:
        raise RuntimeError(f"Environment variable {name} is required")
    return value


def env_bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def database_from_url(url: str) -> dict:
    """postgres://user:password@host:port/name -> Django DATABASES entry."""
    parts = urlparse(url)
    if parts.scheme not in {"postgres", "postgresql"}:
        raise RuntimeError("DATABASE_URL must be a postgres:// URL")
    return {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": parts.path.lstrip("/"),
        "USER": parts.username or "",
        "PASSWORD": parts.password or "",
        "HOST": parts.hostname or "",
        "PORT": str(parts.port or 5432),
        "CONN_MAX_AGE": 60,
    }


SECRET_KEY = env("SECRET_KEY")
# Encrypts users' model API keys at rest (SPEC §2). Generate with
#   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
FERNET_KEY = env("FERNET_KEY")
DEBUG = env_bool("DEBUG", False)
ALLOWED_HOSTS = [h.strip() for h in env("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",") if h]
CSRF_TRUSTED_ORIGINS = [
    o.strip() for o in os.environ.get("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()
]

DATA_DIR = Path(env("DATA_DIR", str(BASE_DIR / "data")))

# Upload limits (SPEC §6.1, assumed in §14).
UPLOAD_MAX_BYTES = 20 * 1024 * 1024
UPLOAD_MAX_ROWS = 100_000
UPLOAD_MAX_COLUMNS = 200
# Per-user rate limits (SPEC §6.4).
RATE_UPLOADS_PER_HOUR = 20
RATE_REVISIONS_PER_HOUR = 60

# Model endpoints. Users supply any OpenAI-compatible base URL. By default the
# server refuses private and loopback addresses so one user cannot make it call
# services on the box or its network; an operator running a local model sets
# ALLOW_PRIVATE_ENDPOINTS=true and accepts that.
ALLOW_PRIVATE_ENDPOINTS = env_bool("ALLOW_PRIVATE_ENDPOINTS", False)
PROVIDER_TIMEOUT_SECONDS = 90
GENERATION_MAX_TOKENS = 8000  # room for reasoning models' hidden tokens plus the spec
GENERATION_SEED = 1
PROMPT_VERSION = "p2026-09-a"
PROMPTS_DIR = BASE_DIR / "prompts"
APP_VERSION = os.environ.get("APP_VERSION", "dev")  # git sha baked in at image build

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "datasets",
    "generation",
    "charts",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "charter.urls"
WSGI_APPLICATION = "charter.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {"default": database_from_url(env("DATABASE_URL"))}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
]

# Registration policy. Email verification switches on when EMAIL_URL is set
# and REQUIRE_EMAIL_VERIFICATION is true; until then registration is open.
EMAIL_URL = os.environ.get("EMAIL_URL", "")
REQUIRE_EMAIL_VERIFICATION = env_bool("REQUIRE_EMAIL_VERIFICATION", False) and bool(EMAIL_URL)

# Sessions and CSRF. The browser talks to /api on the same origin, so the
# cookies stay first-party and SameSite=Lax is enough.
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = False  # the frontend reads it to set X-CSRFToken
SECURE_COOKIES = env_bool("SECURE_COOKIES", False)
SESSION_COOKIE_SECURE = SECURE_COOKIES
CSRF_COOKIE_SECURE = SECURE_COOKIES

# Behind the host reverse proxy (see SPEC §9) the TLS terminates upstream.
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

LANGUAGE_CODE = "en"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"plain": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "plain"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
