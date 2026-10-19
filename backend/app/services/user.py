import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.users import UserRepository

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.user_repo = UserRepository(session)

    async def get_or_create_from_tg(
        self,
        telegram_id: int,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
    ) -> User:
        """Атомарно получает или создаёт пользователя по Telegram ID."""
        user = await self.user_repo.get_or_create(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        await self.session.commit()
        return user

    async def update_profile(
        self,
        user_id: int,
        habr_cookie: str | None = None,
        default_cover_letter: str | None = None,
    ) -> User | None:
        """
        Обновляет куку Хабра и/или дефолтное письмо.
        Возвращает None если пользователь не найден.
        """
        if habr_cookie is None and default_cover_letter is None:
            return await self.user_repo.get_by_id(user_id)

        updated = await self.user_repo.update_profile(
            user_id=user_id,
            habr_cookie=habr_cookie,
            default_cover_letter=default_cover_letter,
        )
        await self.session.commit()
        return updated
