from __future__ import annotations

import re

from app.core.errors import error_codes
from app.core.errors.exceptions import ValidationError
from app.extensions import db
from app.models.user import User
from app.models.username_reservation import UsernameReservation

_USERNAME_RE = re.compile(r"^[a-z0-9](?:[a-z0-9_.]{1,22}[a-z0-9])$")
_RESERVED_USERNAMES = {
    "admin",
    "api",
    "auth",
    "billing",
    "help",
    "login",
    "me",
    "orcaquant",
    "root",
    "security",
    "settings",
    "support",
    "system",
}


class UsernameService:
    def normalize(self, username: str) -> str:
        return str(username or "").strip().lower()

    def validate(self, username: str) -> tuple[str | None, str | None]:
        normalized = self.normalize(username)
        if not normalized:
            return None, "username is required"
        if normalized in _RESERVED_USERNAMES:
            return None, "username is reserved"
        if not _USERNAME_RE.match(normalized):
            return None, "username must be 3-24 chars, lowercase letters, numbers, underscores or dots; it cannot start/end with punctuation"
        if ".." in normalized or "__" in normalized or "._" in normalized or "_." in normalized:
            return None, "username punctuation cannot be repeated or mixed consecutively"
        return normalized, None

    def availability(self, username: str, current_user_id: str | None = None) -> dict:
        normalized, error = self.validate(username)
        if error:
            return {"username": self.normalize(username), "available": False, "reason": error}

        current_user = None
        if current_user_id:
            current_user = db.session.get(User, current_user_id)
            if current_user and current_user.username == normalized:
                return {"username": normalized, "available": True, "reason": "current_username"}

        existing_user = User.query.filter_by(username=normalized).one_or_none()
        if existing_user and existing_user.id != current_user_id:
            return {"username": normalized, "available": False, "reason": "already_taken"}

        reservation = UsernameReservation.query.filter_by(username=normalized).one_or_none()
        if reservation and reservation.user_id != current_user_id:
            return {"username": normalized, "available": False, "reason": "reserved_forever"}
        if reservation and current_user and current_user.username != normalized:
            return {"username": normalized, "available": False, "reason": "reserved_forever"}

        return {"username": normalized, "available": True, "reason": None}

    def claim_for_user(self, user: User, username: str, reason: str = "claimed") -> dict:
        normalized, error = self.validate(username)
        if error:
            raise ValidationError(error)
        availability = self.availability(normalized, current_user_id=user.id)
        if not availability["available"]:
            raise ValidationError("Username is not available", error_code=error_codes.DUPLICATE_RESOURCE_ERROR)

        if user.username == normalized:
            return {"username": normalized, "changed": False}

        reservation = UsernameReservation(username=normalized, user_id=user.id, reason=reason)
        db.session.add(reservation)
        user.username = normalized
        db.session.commit()
        return {"username": normalized, "changed": True}
