from __future__ import annotations

from datetime import datetime, timedelta, timezone
import secrets

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


def _auth_error(message: str, code: str) -> AuthenticationError:
    return AuthenticationError(message, error_code=code)


def create_access_token(subject: str, claims: dict | None = None) -> str:
    now = datetime.now(timezone.utc)
    access_minutes = int(current_app.config.get("JWT_ACCESS_TOKEN_MINUTES", 15)) if has_app_context() else 15
    payload: dict = {"sub": subject, "iat": int(now.timestamp()), "exp": int((now + timedelta(minutes=access_minutes)).timestamp()), "type": "access"}
    if claims:
        payload.update(claims)
    return jwt.encode(payload, _get_secret_key(), algorithm="HS256")


def create_refresh_token(subject: str) -> tuple[str, str]:
    now = datetime.now(timezone.utc)
    refresh_days = int(current_app.config.get("JWT_REFRESH_TOKEN_DAYS", 7)) if has_app_context() else 7
    jti = secrets.token_hex(16)
    payload = {"sub": subject, "iat": int(now.timestamp()), "exp": int((now + timedelta(days=refresh_days)).timestamp()), "type": "refresh", "jti": jti}
    return jwt.encode(payload, _get_secret_key(), algorithm="HS256"), jti


def _decode(token: str) -> dict:
    try:
        return jwt.decode(token, _get_secret_key(), algorithms=["HS256"])
    except ExpiredSignatureError as exc:
        raise _auth_error("Token has expired", error_codes.TOKEN_EXPIRED_ERROR) from exc
    except InvalidTokenError as exc:
        raise _auth_error("Invalid token", error_codes.TOKEN_INVALID_ERROR) from exc


def decode_access_token(token: str) -> dict:
    payload = _decode(token)
    if payload.get("type") != "access":
        raise _auth_error("Invalid token", error_codes.TOKEN_INVALID_ERROR)
    return payload


def decode_refresh_token(token: str) -> dict:
    payload = _decode(token)
    if payload.get("type") != "refresh":
        raise _auth_error("Invalid token", error_codes.TOKEN_INVALID_ERROR)
    return payload
