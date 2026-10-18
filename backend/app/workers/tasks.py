import logging

from app.workers.broker import broker
from app.workers.habr_poller import poll_habr_vacancies

logger = logging.getLogger(__name__)


@broker.task
async def sync_habr_vacancies_task(pages: int = 3) -> int:
    logger.info("Запуск фоновой задачи обновления вакансий с Хабра...")
    count = await poll_habr_vacancies(pages=pages)
    logger.info(f"Фоновая задача завершена. Всего обработано вакансий: {count}")
    return count
