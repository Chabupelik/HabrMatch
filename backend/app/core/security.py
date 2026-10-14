import hashlib
import hmac
import json
from typing import Any
from urllib.parse import parse_qsl

from fastapi import Header, HTTPException, status

from app.core.config import settings


def validate_tg_init_data(init_data: str, bot_token: str) -> dict[str, Any]:
    try:
        parsed_data = dict(parse_qsl(init_data, strict_parsing=True))
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid initData format",
        ) from err

    received_hash = parsed_data.pop("hash", None)
    if not received_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing hash in initData",
        )

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed_data.items()))

    secret_key = hmac.new(
        key=b"WebAppData",
        msg=bot_token.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).digest()

    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode("utf-8"),
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram signature",
        )

    user_raw = parsed_data.get("user")
    if not user_raw:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User data missing in initData",
        )

    user_data: dict[str, Any] = json.loads(user_raw)
    return user_data


async def get_current_tg_user(
    authorization: str | None = Header(default=None),
    x_debug_user_id: int | None = Header(default=None),
) -> dict[str, Any]:
    if settings.DEBUG and x_debug_user_id is not None:
        return {"id": x_debug_user_id, "username": "debug_user"}

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header is missing",
        )

    parts = authorization.split(" ", 1)
    init_data = (
        parts[1] if len(parts) == 2 and parts[0].lower() == "tma" else authorization
    )

    if not settings.BOT_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="BOT_TOKEN is not configured on backend",
        )

    return validate_tg_init_data(init_data=init_data, bot_token=settings.BOT_TOKEN)


async def verify_internal_api_key(
    x_internal_key: str | None = Header(default=None),
) -> None:
    if not x_internal_key or not hmac.compare_digest(
        x_internal_key, settings.INTERNAL_API_KEY
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid internal API key",
        )
