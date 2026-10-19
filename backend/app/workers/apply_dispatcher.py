import asyncio
import logging
import random

import httpx

from app.db.session import async_session_maker
from app.repositories.swipes import SwipeRepository
from app.repositories.users import UserRepository
from app.repositories.vacancies import VacancyRepository

logger = logging.getLogger(__name__)


async def dispatch_habr_apply(
    user_id: int,
    vacancy_id: int,
    swipe_id: int,
    custom_cover_letter: str | None = None,
) -> bool:
    async with async_session_maker() as session:
        user_repo = UserRepository(session)
        vacancy_repo = VacancyRepository(session)
        swipe_repo = SwipeRepository(session)

        user = await user_repo.get_by_id(user_id)
        vacancy = await vacancy_repo.get_by_id(vacancy_id)

        if not user or not user.habr_cookie:
            err = "У пользователя не настроена сессионная кука Хабра"
            logger.warning(f"Apply failed for swipe {swipe_id}: {err}")
            await swipe_repo.update_apply_status(
                swipe_id=swipe_id, is_applied=False, error_message=err
            )
            await session.commit()
            return False

        if not vacancy:
            err = f"Вакансия {vacancy_id} не найдена в БД"
            logger.error(f"Apply failed for swipe {swipe_id}: {err}")
            await swipe_repo.update_apply_status(
                swipe_id=swipe_id, is_applied=False, error_message=err
            )
            await session.commit()
            return False

        cookie = user.habr_cookie
        cover_letter = custom_cover_letter or user.default_cover_letter or ""
        habr_vacancy_id = vacancy.habr_id
        vacancy_url = vacancy.url
        apply_url = vacancy.quick_response_href or "/api/frontend/quick_responses"

    if not apply_url.startswith("http"):
        apply_url = f"https://career.habr.com{apply_url}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:148.0) "
            "Gecko/20100101 Firefox/148.0"
        ),
        "Accept": "application/json",
        "Referer": vacancy_url,
        "Origin": "https://career.habr.com",
        "Cookie": cookie,
    }

    payload = {
        "vacancy_id": habr_vacancy_id,
        "message": cover_letter,
    }

    delay = random.uniform(25.0, 35.0)
    logger.info(
        f"Ожидание {delay:.1f} сек перед откликом на вакансию {habr_vacancy_id} (swipe_id: {swipe_id})..."
    )
    await asyncio.sleep(delay)

    is_success = False
    error_msg: str | None = None

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(apply_url, json=payload, headers=headers)

        if response.status_code in (200, 201):
            logger.info(
                f"Успешный отклик на вакансию {habr_vacancy_id} (swipe_id: {swipe_id})"
            )
            is_success = True
        else:
            error_msg = f"Хабр вернул код {response.status_code}: {response.text[:200]}"
            logger.warning(f"Ошибка отклика для свайпа {swipe_id}: {error_msg}")

    except httpx.TimeoutException as exc:
        error_msg = f"Таймаут при отклике на вакансию {habr_vacancy_id}: {exc}"
        logger.error(error_msg, exc_info=True)
    except httpx.HTTPStatusError as exc:
        error_msg = (
            f"HTTP ошибка: {exc.response.status_code} — {exc.response.text[:200]}"
        )
        logger.error(error_msg, exc_info=True)
    except httpx.RequestError as exc:
        error_msg = f"Сетевая ошибка при отклике: {exc}"
        logger.error(error_msg, exc_info=True)

    async with async_session_maker() as session:
        swipe_repo = SwipeRepository(session)
        await swipe_repo.update_apply_status(
            swipe_id=swipe_id,
            is_applied=is_success,
            error_message=error_msg,
        )
        await session.commit()

    return is_success
