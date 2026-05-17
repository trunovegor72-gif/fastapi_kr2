import re

from pydantic import BaseModel, EmailStr, Field, field_validator


# Задание 3.1
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    age: int | None = None
    is_subscribed: bool | None = None

    @field_validator("age")
    @classmethod
    def age_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("age должен быть положительным числом")
        return v


# Задание 5.1 / 5.2
class LoginData(BaseModel):
    username: str
    password: str


# Задание 5.5
ACCEPT_LANGUAGE_RE = re.compile(
    r"^[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})*(;q=[01](\.\d{1,3})?)?"
    r"(,\s*[a-zA-Z]{1,8}(-[a-zA-Z0-9]{1,8})*(;q=[01](\.\d{1,3})?)?)*$"
)


class CommonHeaders(BaseModel):
    user_agent: str = Field(alias="User-Agent")
    accept_language: str = Field(alias="Accept-Language")

    @field_validator("accept_language")
    @classmethod
    def check_accept_language(cls, v):
        if not ACCEPT_LANGUAGE_RE.match(v):
            raise ValueError("Неверный формат Accept-Language")
        return v
