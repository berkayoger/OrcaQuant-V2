"""Domain exception classes for OrcaQuant."""

from __future__ import annotations

from app.core.errors import error_codes


class OrcaQuantError(Exception):
    """Base exception for domain-safe API errors."""

    status_code = 400
    error_code = "orcaquant_error"

    def __init__(self, message: str, *, status_code: int | None = None, error_code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code or self.status_code
        self.error_code = error_code or self.error_code


class ValidationError(OrcaQuantError):
    status_code = 400
    error_code = error_codes.VALIDATION_ERROR


class AuthenticationError(OrcaQuantError):
    status_code = 401
    error_code = error_codes.AUTHENTICATION_ERROR


class AuthorizationError(OrcaQuantError):
    status_code = 403
    error_code = error_codes.AUTHORIZATION_ERROR


class NotFoundError(OrcaQuantError):
    status_code = 404
    error_code = error_codes.NOT_FOUND_ERROR


class RateLimitError(OrcaQuantError):
    status_code = 429
    error_code = error_codes.RATE_LIMIT_ERROR


class FeatureLockedError(OrcaQuantError):
    status_code = 403
    error_code = error_codes.FEATURE_LOCKED_ERROR
