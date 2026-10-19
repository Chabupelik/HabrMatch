from fastapi import APIRouter, Depends

from app.api.deps import CurrentUserDep, SessionDep
from app.schemas.vacancy import VacancyFilter, VacancyRead
from app.services.vacancy import VacancyService

router = APIRouter(prefix="/vacancies", tags=["Vacancies"])


@router.get(
    "/feed",
    response_model=list[VacancyRead],
    summary="Лента вакансий (непросмотренные)",
)
async def get_vacancy_feed(
    session: SessionDep,
    user: CurrentUserDep,
    filters: VacancyFilter = Depends(),
) -> list[VacancyRead]:
    """
    Возвращает вакансии, которые пользователь ещё не свайпал.

    Фильтры передаются как query-параметры:
    - `qualification`: уровень (junior/middle/senior/lead/intern/all)
    - `is_accredited_only`: только аккредитованные компании
    - `remote_only`: только удалённая работа
    - `min_salary`: минимальная зарплата (по effective_max_salary)
    - `primary_skill`: обязательный скилл
    - `required_skills`: список желаемых скиллов (overlap)
    - `limit`: количество (1–100, по умолчанию 20)
    """
    vacancy_service = VacancyService(session)
    vacancies = await vacancy_service.get_feed(
        user_id=user.id,
        filters=filters,
    )
    return [VacancyRead.model_validate(v) for v in vacancies]
