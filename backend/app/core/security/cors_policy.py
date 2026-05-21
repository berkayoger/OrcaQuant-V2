"""CORS policy helpers."""

from __future__ import annotations

from flask import Flask


def resolve_cors_origins(app: Flask, selected_env: str) -> list[str]:
    origins = app.config.get("CORS_ALLOWED_ORIGINS", []) or []
    normalized = [origin.strip() for origin in origins if origin and origin.strip()]

    if selected_env == "production" and "*" in normalized:
        raise RuntimeError("Wildcard CORS origin is not allowed in production")

    return normalized
