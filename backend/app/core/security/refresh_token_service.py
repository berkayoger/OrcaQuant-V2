"""Refresh token helpers."""

from __future__ import annotations

import hashlib
import hmac
import secrets

from flask import current_app, has_app_context

DEFAULT_SECRET = "dev-refresh-secret"


def _secret() -> str:
    if has_app_context():
        return str(current_app.config.get("SECRET_KEY") or DEFAULT_SECRET)
    return DEFAULT_SECRET


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(48)


def hash_refresh_token(token: str) -> str:
    digest = hmac.new(_secret().encode("utf-8"), token.encode("utf-8"), hashlib.sha256)
    return digest.hexdigest()


def verify_refresh_token(token: str, token_hash: str) -> bool:
    candidate = hash_refresh_token(token)
    return hmac.compare_digest(candidate, token_hash)
