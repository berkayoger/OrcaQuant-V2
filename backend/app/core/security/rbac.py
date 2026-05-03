"""Minimal role-based access control mapping."""

from app.core.security import permissions

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "user": {permissions.ANALYSIS_READ, permissions.ANALYSIS_RUN, permissions.BILLING_READ},
    "admin": {
        permissions.ANALYSIS_READ,
        permissions.ANALYSIS_RUN,
        permissions.BILLING_READ,
        permissions.ADMIN_READ,
        permissions.ADMIN_WRITE,
    },
}


def role_has_permission(role: str, permission: str) -> bool:
    return permission in ROLE_PERMISSIONS.get(role, set())
