from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vacancy import Vacancy
from app.repositories.vacancies import VacancyRepository
from app.schemas.vacancy import VacancyCreate, VacancyFilter


class VacancyService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.vacancy_repo = VacancyRepository(session)

    async def get_feed(
        self,
        user_id: int,
        filters: VacancyFilter,
    ) -> Sequence[Vacancy]:
        """Возвращает непросмотренные вакансии для пользователя с учётом фильтров."""
        return await self.vacancy_repo.get_unseen_for_user(
            user_id=user_id,
            filters=filters,
        )

    async def sync_page(self, vacancies: list[VacancyCreate]) -> int:
        """
        Сохраняет или обновляет страницу вакансий из Хабра (upsert).
        Возвращает число обработанных строк.
        """
        count = await self.vacancy_repo.upsert_many(vacancies)
        await self.session.commit()
        return count
