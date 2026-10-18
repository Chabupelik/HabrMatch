from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        stmt = select(User).where(User.telegram_id == telegram_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        user = await self.get_by_telegram_id(telegram_id)
        if user:
            return user

        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_profile(
        self,
        user_id: int,
        habr_cookie: str | None = None,
        default_cover_letter: str | None = None,
    ) -> User | None:
        values = {}
        if habr_cookie is not None:
            values["habr_cookie"] = habr_cookie
        if default_cover_letter is not None:
            values["default_cover_letter"] = default_cover_letter

        if not values:
            stmt = select(User).where(User.id == user_id)
            res = await self.session.execute(stmt)
            return res.scalar_one_or_none()

        update_stmt = (
            update(User).where(User.id == user_id).values(**values).returning(User)
        )
        result = await self.session.execute(update_stmt)
        await self.session.commit()
        return result.scalar_one_or_none()
