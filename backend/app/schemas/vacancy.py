from datetime import datetime
from enum import StrEnum
from typing import Any

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


class VacancyFilter(BaseModel):
    qualification: QualificationLevel | None = None
    is_accredited_only: bool = False
    remote_only: bool = False
    min_salary: int | None = Field(default=None, ge=0)
    primary_skill: str | None = None
    required_skills: list[str] = Field(default_factory=list)
    limit: int = Field(default=20, ge=1, le=100)
