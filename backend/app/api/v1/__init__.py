from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.swipes import router as swipes_router
from app.api.v1.vacancies import router as vacancies_router

api_v1_router = APIRouter(prefix="/v1")
api_v1_router.include_router(auth_router)
api_v1_router.include_router(swipes_router)
api_v1_router.include_router(vacancies_router)

__all__ = ["api_v1_router"]
