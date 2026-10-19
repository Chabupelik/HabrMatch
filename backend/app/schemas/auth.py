from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, computed_field


class TelegramAuthRequest(BaseModel):
    init_data: str = Field(
        ..., description="initData из window.Telegram.WebApp.initData"
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserBase(BaseModel):
    telegram_id: int = Field(..., description="Telegram ID пользователя")
    username: str | None = Field(None, description="Username в Telegram")
    first_name: str | None = Field(None, description="Имя пользователя")
    last_name: str | None = Field(None, description="Фамилия пользователя")


class UserRead(UserBase):
    """
    Публичное представление пользователя.

    habr_cookie никогда не включается в ответ — только флаг has_habr_cookie.
    """

    id: int
    _habr_cookie: str | None = None

    default_cover_letter: str | None = Field(
        None, description="Дефолтное сопроводительное письмо"
    )
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def has_habr_cookie(self) -> bool:
        """True, если пользователь установил сессионную куку Хабра."""
        return bool(self._habr_cookie)

    @classmethod
    def model_validate(cls, obj: Any, *args: Any, **kwargs: Any) -> "UserRead":  # type: ignore[override]
        instance = super().model_validate(obj, *args, **kwargs)
        if hasattr(obj, "habr_cookie"):
            object.__setattr__(
                instance, "_habr_cookie", getattr(obj, "habr_cookie", None)
            )
        return instance


class UserUpdateProfile(BaseModel):
    habr_cookie: str | None = Field(None, description="Сессионная кука Хабр Карьеры")
    default_cover_letter: str | None = Field(
        None, max_length=4000, description="Дефолтное сопроводительное письмо"
    )
