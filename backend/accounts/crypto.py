"""Fernet wrapper for API keys at rest. The operator holds FERNET_KEY and can
therefore decrypt; the README says so (SPEC §2, secrets at rest)."""

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings


def _fernet() -> Fernet:
    return Fernet(settings.FERNET_KEY.encode())


def encrypt(plaintext: str) -> bytes:
    return _fernet().encrypt(plaintext.encode())


def decrypt(token: bytes) -> str:
    try:
        return _fernet().decrypt(bytes(token)).decode()
    except InvalidToken as exc:
        raise ValueError("Stored key cannot be decrypted with the current FERNET_KEY") from exc
