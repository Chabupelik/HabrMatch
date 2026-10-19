import logging

import httpx

from app.db.session import async_session_maker
from app.services.habr_client import HabrClient
from app.services.vacancy import VacancyService

logger = logging.getLogger(__name__)


async def poll_habr_vacancies(pages: int = 3) -> int:
    """
    Поллинг вакансий с Хабр Карьеры.

    HTTP-запросы и DB-сессия намеренно разделены:
    сессия открывается только на время upsert, а не на всё время парсинга.
    """
    total_saved = 0

    async with HabrClient() as client:
        for page in range(1, pages + 1):
            try:
                logger.info(f"Парсинг Хабр Карьеры: страница {page}/{pages}")

                vacancies = await client.fetch_vacancies_page(page=page)

                if not vacancies:
                    logger.info("Получен пустой список вакансий, завершение.")
                    break

                async with async_session_maker() as session:
                    count = await VacancyService(session).sync_page(vacancies)

                total_saved += count
                logger.info(f"Страница {page}: успешно обработано {count} вакансий.")

            except httpx.HTTPStatusError as e:
                logger.error(
                    f"HTTP-ошибка при парсинге страницы {page}: "
                    f"{e.response.status_code} — {e.response.text[:200]}",
                    exc_info=True,
                )
                break
            except httpx.TimeoutException as e:
                logger.error(
                    f"Таймаут при парсинге страницы {page}: {e}", exc_info=True
                )
                break
            except httpx.RequestError as e:
                logger.error(
                    f"Сетевая ошибка при парсинге страницы {page}: {e}", exc_info=True
                )
                break
            except Exception as e:
                logger.error(
                    f"Неожиданная ошибка при парсинге страницы {page}: {e}",
                    exc_info=True,
                )
                break

    return total_saved
