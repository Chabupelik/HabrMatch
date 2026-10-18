import enum

from sqlalchemy import Enum, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class SwipeAction(enum.StrEnum):
    LIKE = "like"
    DISLIKE = "dislike"


class ApplyStatus(enum.StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    SKIPPED = "skipped"


class Swipe(Base, TimestampMixin):
    __tablename__ = "swipes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    vacancy_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("vacancies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    action: Mapped[SwipeAction] = mapped_column(
        Enum(SwipeAction, name="swipe_action_enum"), nullable=False
    )
    apply_status: Mapped[ApplyStatus] = mapped_column(
        Enum(ApplyStatus, name="apply_status_enum"),
        default=ApplyStatus.SKIPPED,
        nullable=False,
    )

    cover_letter: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="swipes")  # type: ignore[name-defined] # noqa: F821
    vacancy: Mapped["Vacancy"] = relationship("Vacancy", back_populates="swipes")  # type: ignore[name-defined] # noqa: F821

    __table_args__ = (
        UniqueConstraint("user_id", "vacancy_id", name="uq_user_vacancy_swipe"),
    )
