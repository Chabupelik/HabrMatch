from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.swipe import ApplyStatus, Swipe
from app.models.swipe import SwipeAction as ModelSwipeAction
from app.schemas.apply import SwipeAction as SchemaSwipeAction


class SwipeRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def record_swipe(
        self,
        user_id: int,
        vacancy_id: int,
        action: SchemaSwipeAction | ModelSwipeAction,
        cover_letter: str | None = None,
    ) -> Swipe:
        is_like = action == SchemaSwipeAction.LIKE or action == ModelSwipeAction.LIKE
        db_action = ModelSwipeAction.LIKE if is_like else ModelSwipeAction.DISLIKE
        apply_status = ApplyStatus.PENDING if is_like else ApplyStatus.SKIPPED

        swipe = Swipe(
            user_id=user_id,
            vacancy_id=vacancy_id,
            action=db_action,
            apply_status=apply_status,
            cover_letter=cover_letter,
        )
        self.session.add(swipe)
        await self.session.commit()
        await self.session.refresh(swipe)
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
        await self.session.commit()

    async def get_by_user_and_vacancy(
        self, user_id: int, vacancy_id: int
    ) -> Swipe | None:
        stmt = select(Swipe).where(
            Swipe.user_id == user_id, Swipe.vacancy_id == vacancy_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
