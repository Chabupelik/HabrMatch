import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import SwipeAction
from app.models.swipe import Swipe
from app.repositories.swipes import SwipeRepository
from app.schemas.apply import SwipeCreate
from app.workers.tasks import apply_to_vacancy_task

logger = logging.getLogger(__name__)


class ApplyService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.swipe_repo = SwipeRepository(session)

    async def handle_swipe(self, user_id: int, swipe_data: SwipeCreate) -> Swipe:
        existing_swipe = await self.swipe_repo.get_by_user_and_vacancy(
            user_id=user_id,
            vacancy_id=swipe_data.vacancy_id,
        )
        if existing_swipe:
            return existing_swipe

        swipe = await self.swipe_repo.record_swipe(
            user_id=user_id,
            vacancy_id=swipe_data.vacancy_id,
            action=swipe_data.action,
            cover_letter=swipe_data.cover_letter,
        )

        # Commit здесь — Unit of Work: репозиторий только накапливает, сервис коммитит.
        await self.session.commit()
        await self.session.refresh(swipe)

        if swipe_data.action == SwipeAction.LIKE:
            try:
                await apply_to_vacancy_task.kiq(
                    user_id=user_id,
                    vacancy_id=swipe_data.vacancy_id,
                    swipe_id=swipe.id,
                    custom_cover_letter=swipe_data.cover_letter,
                )
                logger.info(
                    f"Задача на отклик отправлена в очередь для swipe_id={swipe.id}"
                )
            except (ConnectionError, TimeoutError, OSError) as e:
                # Ловим только транспортные ошибки брокера; системные исключения пробрасываем.
                logger.error(
                    f"Не удалось отправить задачу отклика в Taskiq: {e}", exc_info=True
                )
                try:
                    await self.swipe_repo.update_apply_status(
                        swipe_id=swipe.id,
                        is_applied=False,
                        error_message=f"Queue dispatch error: {e}",
                    )
                    await self.session.commit()
                except Exception:
                    logger.exception(
                        "Ошибка при обновлении статуса свайпа после сбоя очереди"
                    )

        return swipe
