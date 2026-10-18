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
    habr_id: int = Field(..., description="Уникальный ID вакансии на Хабр Карьере")
    title: str = Field(..., max_length=255, description="Название вакансии")
    company_title: str = Field(..., max_length=255, description="Название компании")
    company_href: str | None = Field(
        None, description="Относительный или полный URL компании"
    )

    is_accredited: bool = Field(
        default=False, description="Аккредитованная IT-компания"
    )
    remote_work: bool = Field(default=False, description="Доступна ли удаленная работа")
    relocation: bool = Field(default=False, description="Помощь с релокацией")

    salary_min: int | None = Field(None, ge=0, description="Минимальная зарплата")
    salary_max: int | None = Field(None, ge=0, description="Максимальная зарплата")
    salary_currency: str | None = Field(
        None, max_length=10, description="Валюта (RUR, USD и т.д.)"
    )
    effective_max_salary: int | None = Field(
        None,
        ge=0,
        description="Эффективный потолок зарплаты для сортировки и фильтрации",
    )

    qualification: str | None = Field(None, description="Грейд (junior, middle, etc.)")
    skills: list[str] = Field(
        default_factory=list, description="Список тегов стека/навыков"
    )
    locations: list[str] = Field(default_factory=list, description="Города / локации")

    url: str = Field(..., description="Прямая ссылка на вакансию на Хабре")
    cover_letter_required: bool = Field(
        default=False, description="Требуется ли обязательное сопроводительное письмо"
    )
    published_at: datetime | None = Field(None, description="Дата публикации вакансии")


class VacancyCreate(VacancyBase):
    description_text: str | None = Field(
        default=None, description="Полное текстовое описание вакансии"
    )
    raw_payload: dict[str, Any] = Field(
        default_factory=dict,
        description="Сырой JSON с Хабра на случай изменения структуры",
    )


class VacancyRead(VacancyBase):
    id: int = Field(..., description="Внутренний primary key вакансии в нашей БД")
    created_at: datetime

    description_preview: str | None = Field(
        None, description="Краткая выжимка описания вакансии"
    )

    model_config = ConfigDict(from_attributes=True)


class VacancyFilter(BaseModel):
    qualification: QualificationLevel | None = Field(
        default=None,
        description="Фильтр по грейду (junior, middle, etc.)",
    )
    is_accredited_only: bool = Field(
        default=False,
        description="Показывать только аккредитованные IT-компании",
    )
    remote_only: bool = Field(
        default=False,
        description="Только удаленная работа",
    )
    min_salary: int | None = Field(
        default=None,
        ge=0,
        description="Минимальный порог зарплаты",
    )
    primary_skill: str | None = Field(
        default=None,
        description="Обязательный основной навык (100% должен присутствовать, например 'python')",
    )
    required_skills: list[str] = Field(
        default_factory=list,
        description="Сопутствующие технологии/фреймворки (хотя бы один из списка)",
    )
    limit: int = Field(
        default=20, ge=1, le=100, description="Количество карточек в батче"
    )
