"""
Единый источник правды для всех enum-значений приложения.
Импортировать отсюда во все модели, схемы и репозитории.
"""

import enum


class SwipeAction(enum.StrEnum):
    """Действие пользователя при свайпе вакансии."""

    LIKE = "like"
    DISLIKE = "dislike"


class ApplyStatus(enum.StrEnum):
    """Статус автоотклика на вакансию."""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    SKIPPED = "skipped"
