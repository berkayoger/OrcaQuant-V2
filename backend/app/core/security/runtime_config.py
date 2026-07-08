"""Runtime configuration validation helpers."""

from __future__ import annotations

from urllib.parse import urlparse

from flask import Flask

SUPPORTED_BILLING_PROVIDERS = {"fake", "iyzico"}
_PLACEHOLDER_VALUES = {"", "placeholder", "change-me", "set-me", "todo"}
_PRODUCTION_LOCAL_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0"}


def validate_runtime_config(app: Flask, selected_env: str) -> None:
    _validate_positive_int(app, "JWT_ACCESS_TOKEN_MINUTES")
    _validate_positive_int(app, "JWT_REFRESH_TOKEN_DAYS")
    _validate_positive_int(app, "MAX_CONTENT_LENGTH")
    _validate_positive_int(app, "MARKET_DATA_TIMEOUT_SECONDS")
    _validate_positive_int(app, "MARKET_DATA_CACHE_TTL_SECONDS")
    _validate_positive_int(app, "PAYMENT_PROVIDER_TIMEOUT_SECONDS")

    allowed = app.config.get("CORS_ALLOWED_ORIGINS", []) or []
    if not allowed:
        raise RuntimeError("CORS_ALLOWED_ORIGINS must contain at least one origin")

    for origin in allowed:
        _validate_http_url(origin, f"Invalid CORS origin format: {origin}")

    if selected_env == "production" and app.config.get("SECRET_KEY") == "dev-secret":
        raise RuntimeError("SECRET_KEY must not use development default in production")

    _validate_billing_config(app, selected_env)


def _validate_positive_int(app: Flask, key: str) -> None:
    value = app.config.get(key)
    if not isinstance(value, int) or value <= 0:
        raise RuntimeError(f"{key} must be a positive integer")


def _validate_http_url(value: str, message: str) -> None:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise RuntimeError(message)


def _is_missing(value: object) -> bool:
    return str(value or "").strip().lower() in _PLACEHOLDER_VALUES


def _validate_billing_config(app: Flask, selected_env: str) -> None:
    provider = str(app.config.get("BILLING_PROVIDER", "fake")).strip().lower()
    if provider not in SUPPORTED_BILLING_PROVIDERS:
        supported = ", ".join(sorted(SUPPORTED_BILLING_PROVIDERS))
        raise RuntimeError(f"BILLING_PROVIDER must be one of: {supported}")

    allowed_currencies = app.config.get("BILLING_ALLOWED_CURRENCIES", []) or []
    if not allowed_currencies:
        raise RuntimeError("BILLING_ALLOWED_CURRENCIES must contain at least one currency")

    billing_url_keys = ["BILLING_CHECKOUT_SUCCESS_URL", "BILLING_CHECKOUT_FAILURE_URL", "BILLING_CALLBACK_URL"]
    for key in billing_url_keys:
        _validate_http_url(str(app.config.get(key) or ""), f"{key} must be a valid http(s) URL")

    billing_enabled = bool(app.config.get("ENABLE_BILLING", False))
    if not billing_enabled:
        return

    if selected_env == "production":
        for key in billing_url_keys:
            parsed = urlparse(str(app.config.get(key) or ""))
            if parsed.hostname in _PRODUCTION_LOCAL_HOSTS:
                raise RuntimeError(f"{key} must not point to localhost in production")

    if selected_env == "production" and provider == "fake":
        raise RuntimeError("BILLING_PROVIDER=fake is not allowed when ENABLE_BILLING=true in production")

    if provider == "iyzico":
        missing = [key for key in ["IYZICO_API_KEY", "IYZICO_SECRET", "IYZICO_BASE_URL"] if _is_missing(app.config.get(key))]
        if selected_env == "production" and missing:
            raise RuntimeError(f"Iyzico billing is missing required settings: {', '.join(missing)}")
