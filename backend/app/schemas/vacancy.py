from datetime import datetime
from enum import StrEnum
from typing import Any

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field


class QualificationLevel(StrEnum):
    ALL = "all"
    INTERN = "intern"
    JUNIOR = "junior"
    MIDDLE = "middle"
    SENIOR = "senior"
    LEAD = "lead"


class VacancyBase(BaseModel):
    habr_id: int
    title: str
    url: str
    qualification: str | None = None
    employment: str | None = None
    remote_work: bool = False
    is_marked: bool = False
    published_date_raw: str | None = None

    company_id: int | None = None
    company_title: str
    company_alias: str | None = None
    company_url: str | None = None
    company_logo: str | None = None
    is_accredited: bool = False
    company_rating: str | None = None

    salary_from: int | None = None
    salary_to: int | None = None
    salary_currency: str | None = None
    salary_formatted: str | None = None

    predicted_salary_from: int | None = None
    predicted_salary_to: int | None = None
    effective_max_salary: int | None = None

    skills: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)
    divisions: list[str] = Field(default_factory=list)

    can_quick_response: bool = False
    quick_response_href: str | None = None


class VacancyCreate(VacancyBase):
    raw_data: dict[str, Any] | None = None


class VacancyRead(VacancyBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VacancyFilter:
    """Контейнер параметров фильтрации ленты вакансий из Query-строки."""

    def __init__(
        self,
        qualification: QualificationLevel | None = Query(
            default=None,
            description="Уровень квалификации",
        ),
        is_accredited_only: bool = Query(
            default=False,
            description="Только аккредитованные IT-компании",
        ),
        remote_only: bool = Query(
            default=False,
            description="Только удаленный формат работы",
        ),
        min_salary: int | None = Query(
            default=None,
            ge=0,
            description="Минимальная зарплата",
        ),
        primary_skill: str | None = Query(
            default=None,
            description="Ключевой навык (поиск точного вхождения)",
        ),
        required_skills: list[str] = Query(
            default=[],
            description="Список навыков для пересечения (overlap)",
        ),
        limit: int = Query(
            default=20,
            ge=1,
            le=100,
            description="Количество записей в ответе",
        ),
    ):
        self.qualification = qualification
        self.is_accredited_only = is_accredited_only
        self.remote_only = remote_only
        self.min_salary = min_salary
        self.primary_skill = primary_skill
        self.required_skills = required_skills
        self.limit = limit
