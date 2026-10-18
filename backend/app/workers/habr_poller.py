import logging

from app.db.session import async_session_maker
from app.repositories.vacancies import VacancyRepository
from app.services.habr_client import HabrClient

logger = logging.getLogger(__name__)


async def poll_habr_vacancies(pages: int = 3) -> int:
    client = HabrClient()
    total_saved = 0

    async with async_session_maker() as session:
        repo = VacancyRepository(session)

        for page in range(1, pages + 1):
            try:
                logger.info(f"Парсинг Хабр Карьеры: страница {page}/{pages}")
                vacancies = await client.fetch_vacancies_page(page=page)

                if not vacancies:
                    logger.info("Получен пустой список вакансий, завершение.")
                    break

                count = await repo.upsert_many(vacancies)
                total_saved += count
                logger.info(f"Страница {page}: успешно обработано {count} вакансий.")
            except Exception as e:
                logger.error(f"Ошибка при парсинге страницы {page}: {e}", exc_info=True)
                break

    return total_saved
