from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.enums import ApplyStatus, SwipeAction
from app.models.swipe import Swipe


class SwipeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def record_swipe(
        self,
        user_id: int,
        vacancy_id: int,
        action: SwipeAction,
        cover_letter: str | None = None,
    ) -> Swipe:
        is_like = action == SwipeAction.LIKE
        apply_status = ApplyStatus.PENDING if is_like else ApplyStatus.SKIPPED

        swipe = Swipe(
            user_id=user_id,
            vacancy_id=vacancy_id,
            action=action,
            apply_status=apply_status,
            cover_letter=cover_letter,
        )
        self.session.add(swipe)
        # Commit/flush делается на уровне сервиса (Unit of Work).
        return swipe

    async def update_apply_status(
        self,
        swipe_id: int,
        is_applied: bool,
        error_message: str | None = None,
    ) -> None:
        stmt = (
            update(Swipe)
            .where(Swipe.id == swipe_id)
            .values(
                apply_status=ApplyStatus.SENT if is_applied else ApplyStatus.FAILED,
                error_message=error_message,
            )
        )
        await self.session.execute(stmt)
        # Commit/flush делается на уровне сервиса (Unit of Work).

    async def get_by_user_and_vacancy(
        self, user_id: int, vacancy_id: int
    ) -> Swipe | None:
        stmt = select(Swipe).where(
            Swipe.user_id == user_id, Swipe.vacancy_id == vacancy_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
