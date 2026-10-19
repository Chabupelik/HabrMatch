from fastapi import APIRouter, status

from app.api.deps import CurrentUserDep, SessionDep
from app.schemas.apply import SwipeCreate, SwipeResponse
from app.services.apply import ApplyService

router = APIRouter(prefix="/swipes", tags=["Swipes"])


@router.post("", response_model=SwipeResponse, status_code=status.HTTP_201_CREATED)
async def create_swipe(
    swipe_in: SwipeCreate,
    session: SessionDep,
    user: CurrentUserDep,
) -> SwipeResponse:
    """
    Фиксирует свайп (лайк/дизлайк).
    При лайке автоматически отправляет задачу отклика в Taskiq/RabbitMQ.
    """
    apply_service = ApplyService(session)
    swipe = await apply_service.handle_swipe(
        user_id=user.id,
        swipe_data=swipe_in,
    )
    return SwipeResponse.model_validate(swipe)
