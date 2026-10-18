from sqlalchemy import BigInteger, Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, nullable=False
    )
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(128), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    habr_cookie: Mapped[str | None] = mapped_column(Text, nullable=True)

    default_cover_letter: Mapped[str | None] = mapped_column(Text, nullable=True)

    swipes: Mapped[list["Swipe"]] = relationship(  # type: ignore[name-defined] # noqa: F821
        "Swipe", back_populates="user", cascade="all, delete-orphan"
    )
