"""Admin guard helper."""

from app.core.errors.exceptions import AuthorizationError


def require_admin_user(user: dict) -> None:
    if not user or user.get("role") != "admin":
        raise AuthorizationError("Admin privileges required")
