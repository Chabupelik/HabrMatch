import logging

from app.workers.broker import broker

logger = logging.getLogger(__name__)


@broker.task
async def parse_habr_orders_task() -> str:
    logger.info("Запуск фоновой задачи парсинга заказов с Хабра...")
    return "Парсинг успешно завершен"


@broker.task
async def send_tg_notification_task(chat_id: int, message: str) -> None:
    logger.info(f"Отправка уведомления пользователю {chat_id}: {message}")
