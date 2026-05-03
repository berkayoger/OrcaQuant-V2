"""JWT access token service."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app, has_app_context
from jwt import ExpiredSignatureError, InvalidTokenError

from app.core.errors import error_codes
from app.core.errors.exceptions import AuthenticationError

DEFAULT_SECRET = "dev-insecure-secret"


def _get_secret_key() -> str:
    if has_app_context():
        return str(current_app.config.get("SECRET_KEY") or DEFAULT_SECRET)
    return DEFAULT_SECRET


def create_access_token(subject: str, claims: dict | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload: dict = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=15)).timestamp()),
        "type": "access",
    }
    if claims:
        payload.update(claims)
    return jwt.encode(payload, _get_secret_key(), algorithm="HS256")


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, _get_secret_key(), algorithms=["HS256"])
    except ExpiredSignatureError as exc:
        raise AuthenticationError("Token has expired", error_code=error_codes.TOKEN_EXPIRED_ERROR) from exc
    except InvalidTokenError as exc:
        raise AuthenticationError("Invalid token", error_code=error_codes.TOKEN_INVALID_ERROR) from exc

    if payload.get("type") != "access":
        raise AuthenticationError("Invalid token", error_code=error_codes.TOKEN_INVALID_ERROR)
    return payload
