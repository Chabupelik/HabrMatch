from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.enums import SwipeAction

__all__ = ["SwipeAction", "SwipeCreate", "SwipeResponse"]


class SwipeCreate(BaseModel):
    vacancy_id: int = Field(
        ..., description="ID вакансии из нашей БД, которую свайпнули"
    )
    action: SwipeAction = Field(
        ...,
        description="Тип действия: 'like' (откликнуться) или 'dislike' (пропустить)",
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
