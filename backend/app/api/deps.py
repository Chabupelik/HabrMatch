from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user_payload
from app.db.session import async_session_maker
from app.models.user import User
from app.services.user import UserService


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db)]
AuthPayloadDep = Annotated[dict, Depends(get_current_user_payload)]


async def get_current_user(
    session: SessionDep,
    payload: AuthPayloadDep,
) -> User:
    telegram_id = payload.get("id")
    if not telegram_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректные данные авторизации Telegram",
        )

    user_service = UserService(session)
    return await user_service.get_or_create_from_tg(
        telegram_id=telegram_id,
        username=payload.get("username"),
        first_name=payload.get("first_name"),
        last_name=payload.get("last_name"),
    )


CurrentUserDep = Annotated[User, Depends(get_current_user)]
