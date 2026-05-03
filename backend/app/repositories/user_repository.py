"""Temporary in-memory user repository for Sprint 2."""

from __future__ import annotations

import uuid

from app.core.errors import error_codes
from app.core.errors.exceptions import ValidationError


class UserRepository:
    def __init__(self) -> None:
        self._users_by_id: dict[str, dict] = {}
        self._id_by_email: dict[str, str] = {}

    def create_user(self, email: str, password_hash: str) -> dict:
        key = email.lower()
        if key in self._id_by_email:
            raise ValidationError("Email already registered", error_code=error_codes.DUPLICATE_RESOURCE_ERROR)

        user_id = str(uuid.uuid4())
        user = {
            "id": user_id,
            "email": key,
            "password_hash": password_hash,
            "role": "user",
            "is_active": True,
        }
        self._users_by_id[user_id] = user
        self._id_by_email[key] = user_id
        return dict(user)

    def get_by_email(self, email: str) -> dict | None:
        user_id = self._id_by_email.get(email.lower())
        if not user_id:
            return None
        return dict(self._users_by_id[user_id])

    def get_by_id(self, user_id: str) -> dict | None:
        user = self._users_by_id.get(user_id)
        return dict(user) if user else None
