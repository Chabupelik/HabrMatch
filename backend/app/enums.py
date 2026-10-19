import enum


class SwipeAction(enum.StrEnum):
    LIKE = "like"
    DISLIKE = "dislike"


class ApplyStatus(enum.StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    SKIPPED = "skipped"
