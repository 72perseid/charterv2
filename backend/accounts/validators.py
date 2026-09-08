from django.core.exceptions import ValidationError
from django.core.validators import validate_email


def clean_email(value: str) -> str:
    """Pydantic field validator that reuses Django's email rules."""
    value = value.strip().lower()
    try:
        validate_email(value)
    except ValidationError as exc:
        raise ValueError("Enter a valid email address.") from exc
    return value
