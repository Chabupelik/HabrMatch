from typing import Any

from sqlalchemy import BigInteger, Boolean, Index, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Vacancy(Base, TimestampMixin):
    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    habr_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, nullable=False
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(512), nullable=False)
    qualification: Mapped[str | None] = mapped_column(String(64), nullable=True)
    employment: Mapped[str | None] = mapped_column(String(64), nullable=True)
    remote_work: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_marked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    published_date_raw: Mapped[str | None] = mapped_column(String(64), nullable=True)

    company_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    company_title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company_alias: Mapped[str | None] = mapped_column(String(128), nullable=True)
    company_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    company_logo: Mapped[str | None] = mapped_column(String(512), nullable=True)
    is_accredited: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )
    company_rating: Mapped[str | None] = mapped_column(String(32), nullable=True)

    salary_from: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_to: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str | None] = mapped_column(String(16), nullable=True)
    salary_formatted: Mapped[str | None] = mapped_column(String(128), nullable=True)

    predicted_salary_from: Mapped[int | None] = mapped_column(Integer, nullable=True)
    predicted_salary_to: Mapped[int | None] = mapped_column(Integer, nullable=True)

    effective_max_salary: Mapped[int | None] = mapped_column(
        Integer, nullable=True, index=True
    )

    skills: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list, nullable=False
    )
    locations: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list, nullable=False
    )
    divisions: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list, nullable=False
    )

    can_quick_response: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    quick_response_href: Mapped[str | None] = mapped_column(String(512), nullable=True)
    raw_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    swipes: Mapped[list["Swipe"]] = relationship(  # type: ignore[name-defined] # noqa: F821
        "Swipe", back_populates="vacancy", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("ix_vacancies_accredited_remote", "is_accredited", "remote_work"),
    )
