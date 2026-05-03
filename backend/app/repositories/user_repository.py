from __future__ import annotations

from app.core.errors import error_codes
from app.core.errors.exceptions import ValidationError
from app.extensions import db
from app.models.user import User


class UserRepository:
    def create_user(self, email: str, password_hash: str) -> dict:
        key = email.lower()
        if self.get_by_email(key):
            raise ValidationError("Email already registered", error_code=error_codes.DUPLICATE_RESOURCE_ERROR)

        user = User(email=key, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        return self._to_dict(user)

    def get_by_email(self, email: str) -> dict | None:
        user = User.query.filter_by(email=email.lower()).one_or_none()
        return self._to_dict(user) if user else None

    def get_by_id(self, user_id: str) -> dict | None:
        user = User.query.filter_by(id=user_id).one_or_none()
        return self._to_dict(user) if user else None

    def _to_dict(self, user: User) -> dict:
        return {
            "id": user.id,
            "email": user.email,
            "password_hash": user.password_hash,
            "role": user.role,
            "is_active": user.is_active,
        }
