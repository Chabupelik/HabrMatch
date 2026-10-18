import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

logger = logging.getLogger(__name__)

app = FastAPI(title="HabrSwipe API", version="0.1.0")

# В DEBUG-режиме разрешаем все origins (локальная разработка).
# На проде обязательно задать явный список в ALLOWED_ORIGINS.
_ALLOWED_ORIGINS: list[str] = (
    ["*"]
    if settings.DEBUG
    else [
        "https://your-frontend.com",  # TODO: заменить на реальный домен в .env
        "https://t.me",
    ]
)

if settings.DEBUG:
    logger.warning(
        "DEBUG=True: CORS открыт для всех origins и аутентификация ослаблена! "
        "Не использовать в продакшене."
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=_ALLOWED_ORIGINS,
    # allow_credentials=True несовместимо с allow_origins=["*"] по спецификации W3C,
    # поэтому credentials включаем только на проде с явным списком origins.
    allow_credentials=not settings.DEBUG,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "X-Internal-Key",
        "X-Debug-User-Id",
    ],
)


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "app": "HabrSwipe Backend"}
