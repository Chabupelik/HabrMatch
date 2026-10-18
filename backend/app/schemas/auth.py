from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


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
    id: int
    has_habr_cookie: bool = Field(
        default=False, description="Установлена ли сессионная кука Хабра"
    )
    default_cover_letter: str | None = Field(
        None, description="Дефолтное сопроводительное письмо"
    )
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdateProfile(BaseModel):
    habr_cookie: str | None = Field(None, description="Сессионная кука Хабр Карьеры")
    default_cover_letter: str | None = Field(
        None, max_length=4000, description="Дефолтное сопроводительное письмо"
    )
