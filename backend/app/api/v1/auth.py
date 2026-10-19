from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUserDep, SessionDep
from app.schemas.auth import UserRead, UserUpdateProfile
from app.services.user import UserService

router = APIRouter(prefix="/auth", tags=["Auth & Profile"])


@router.get(
    "/me",
    response_model=UserRead,
    summary="Получить профиль текущего пользователя",
)
async def get_current_user_profile(user: CurrentUserDep) -> UserRead:
    """
    Возвращает данные профиля, идентифицированного через Telegram initData.

    Если пользователь ещё не существует в БД — создаётся автоматически
    (через `get_or_create` в dependency `CurrentUserDep`).
    """
    return UserRead.model_validate(user)


@router.patch(
    "/me",
    response_model=UserRead,
    summary="Обновить профиль: кука Хабра / дефолтное письмо",
)
async def update_user_profile(
    profile_data: UserUpdateProfile,
    session: SessionDep,
    user: CurrentUserDep,
) -> UserRead:
    """
    Сохраняет сессионную куку Хабра и/или дефолтное сопроводительное письмо.

    Передай только те поля, которые хочешь изменить — остальные останутся прежними.
    """
    user_service = UserService(session)
    updated_user = await user_service.update_profile(
        user_id=user.id,
        habr_cookie=profile_data.habr_cookie,
        default_cover_letter=profile_data.default_cover_letter,
    )

    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    return UserRead.model_validate(updated_user)
