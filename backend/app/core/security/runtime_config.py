"""Runtime configuration validation helpers."""

from __future__ import annotations

from urllib.parse import urlparse

from flask import Flask


def validate_runtime_config(app: Flask, selected_env: str) -> None:
    _validate_positive_int(app, "JWT_ACCESS_TOKEN_MINUTES")
    _validate_positive_int(app, "JWT_REFRESH_TOKEN_DAYS")
    _validate_positive_int(app, "MAX_CONTENT_LENGTH")

    allowed = app.config.get("CORS_ALLOWED_ORIGINS", []) or []
    if not allowed:
        raise RuntimeError("CORS_ALLOWED_ORIGINS must contain at least one origin")

    for origin in allowed:
        parsed = urlparse(origin)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise RuntimeError(f"Invalid CORS origin format: {origin}")

    if selected_env == "production" and app.config.get("SECRET_KEY") == "dev-secret":
        raise RuntimeError("SECRET_KEY must not use development default in production")


def _validate_positive_int(app: Flask, key: str) -> None:
    value = app.config.get(key)
    if not isinstance(value, int) or value <= 0:
        raise RuntimeError(f"{key} must be a positive integer")
