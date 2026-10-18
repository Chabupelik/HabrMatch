from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class SwipeAction(StrEnum):
    LIKE = "like"
    SKIP = "skip"


class SwipeCreate(BaseModel):
    vacancy_id: int = Field(
        ..., description="ID вакансии из нашей БД, которую свайпнули"
    )
    action: SwipeAction = Field(
        ..., description="Тип действия: 'like' (откликнуться) или 'skip' (пропустить)"
    )
    cover_letter: str | None = Field(
        default=None,
        max_length=4000,
        description="Кастомное сопроводительное письмо (если None, берётся дефолтное из профиля)",
    )


class SwipeResponse(BaseModel):
    id: int = Field(..., description="ID записи свайпа в БД")
    vacancy_id: int
    user_id: int
    action: SwipeAction
    is_applied: bool = Field(
        default=False,
        description="Была ли задача на автоотклик успешно отправлена в очередь RabbitMQ",
    )
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
