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
