
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from jwt import InvalidTokenError

from app.core.config import settings


ALGORITHM = settings.JWT_ALGORITHM


def create_access_token(user_id: uuid.UUID) -> tuple[str, int]:
    expires_in = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    now = datetime.now(timezone.utc)

    payload = {
        "sub": str(user_id),
        "type": "access",
        "jti": str(uuid.uuid4()),
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }

    token = jwt.encode(
        payload,
        settings.JWT_ACCESS_SECRET.get_secret_value(),
        algorithm=ALGORITHM,
    )

    return token, expires_in


def create_refresh_token(
    user_id: uuid.UUID,
    jti: uuid.UUID | None = None,
) -> tuple[str, uuid.UUID, datetime]:
    token_id = jti or uuid.uuid4()
    now = datetime.now(timezone.utc)
    expires_at = now + timedelta(
        days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    )

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "jti": str(token_id),
        "iat": now,
        "exp": expires_at,
    }

    token = jwt.encode(
        payload,
        settings.JWT_REFRESH_SECRET.get_secret_value(),
        algorithm=ALGORITHM,
    )

    return token, token_id, expires_at


def decode_access_token(token: str) -> dict:
    payload = jwt.decode(
        token,
        settings.JWT_ACCESS_SECRET.get_secret_value(),
        algorithms=[ALGORITHM],
        options={"require": ["exp", "iat", "sub", "jti"]},
    )

    if payload.get("type") != "access":
        raise InvalidTokenError("Invalid access token")

    return payload


def decode_refresh_token(token: str) -> dict:
    payload = jwt.decode(
        token,
        settings.JWT_REFRESH_SECRET.get_secret_value(),
        algorithms=[ALGORITHM],
        options={"require": ["exp", "iat", "sub", "jti"]},
    )

    if payload.get("type") != "refresh":
        raise InvalidTokenError("Invalid refresh token")

    return payload
