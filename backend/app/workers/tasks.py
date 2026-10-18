import logging

from app.workers.apply_dispatcher import dispatch_habr_apply
from app.workers.broker import broker
from app.workers.habr_poller import poll_habr_vacancies

logger = logging.getLogger(__name__)


@broker.task
async def sync_habr_vacancies_task(pages: int = 3) -> int:
    logger.info("Запуск фоновой задачи обновления вакансий с Хабра...")
    count = await poll_habr_vacancies(pages=pages)
    logger.info(f"Фоновая задача завершена. Всего обработано вакансий: {count}")
    return count


@broker.task
async def apply_to_vacancy_task(
    user_id: int,
    vacancy_id: int,
    swipe_id: int,
    custom_cover_letter: str | None = None,
) -> bool:
    logger.info(
        f"Запуск задачи отклика: user={user_id}, vacancy={vacancy_id}, swipe={swipe_id}"
    )
    return await dispatch_habr_apply(
        user_id=user_id,
        vacancy_id=vacancy_id,
        swipe_id=swipe_id,
        custom_cover_letter=custom_cover_letter,
    )
