from datetime import datetime
from uuid import UUID

from ninja import Schema
from pydantic import Field, field_validator

from accounts.validators import clean_email


class RegisterIn(Schema):
    email: str
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(default="", max_length=120)

    _email = field_validator("email")(clean_email)


class LoginIn(Schema):
    email: str
    password: str

    _email = field_validator("email")(clean_email)


class UserOut(Schema):
    id: UUID
    email: str
    display_name: str


class Detail(Schema):
    detail: str


class ModelConfigIn(Schema):
    base_url: str = Field(min_length=8, max_length=500)
    model: str = Field(min_length=1, max_length=200)
    api_key: str = Field(default="", max_length=1000)  # blank keeps the stored key
    temperature: float = Field(default=0.0, ge=0.0, le=2.0)


class ModelConfigOut(Schema):
    base_url: str
    model: str
    temperature: float
    has_key: bool
    key_hint: str
    updated_at: datetime | None


class ModelTestOut(Schema):
    ok: bool
    message: str
    model: str | None = None
    duration_ms: int | None = None


class ModelListIn(Schema):
    base_url: str = Field(min_length=8, max_length=500)
    api_key: str = Field(default="", max_length=1000)  # blank uses the stored key


class ModelListOut(Schema):
    models: list[str]
