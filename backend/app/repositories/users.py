from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

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
        """Атомарный upsert — защищён от race condition при параллельных запросах."""
        stmt = (
            pg_insert(User)
            .values(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
            )
            .on_conflict_do_nothing(index_elements=["telegram_id"])
            .returning(User)
        )
        result = await self.session.execute(stmt)
        # Commit/flush делается на уровне сервиса (Unit of Work).
        user = result.scalar_one_or_none()

        if user is None:
            # ON CONFLICT DO NOTHING сработал — запись уже есть, читаем её
            user = await self.get_by_telegram_id(telegram_id)

        return user  # type: ignore[return-value]

    async def update_profile(
        self,
        user_id: int,
        habr_cookie: str | None = None,
        default_cover_letter: str | None = None,
    ) -> User | None:
        values: dict[str, object] = {}
        if habr_cookie is not None:
            values["habr_cookie"] = habr_cookie
        if default_cover_letter is not None:
            values["default_cover_letter"] = default_cover_letter

        if not values:
            return await self.get_by_id(user_id)

        stmt = update(User).where(User.id == user_id).values(**values).returning(User)
        result = await self.session.execute(stmt)
        # Commit/flush делается на уровне сервиса (Unit of Work).
        return result.scalar_one_or_none()
