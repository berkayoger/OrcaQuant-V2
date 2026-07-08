from __future__ import annotations

from app.core.errors import error_codes
from app.core.errors.exceptions import ValidationError
from app.extensions import db
from app.models.plan import Plan
from app.models.user import User
from app.models.username_reservation import UsernameReservation
from app.services.account.username_service import UsernameService


class UserRepository:
    def __init__(self, username_service: UsernameService | None = None) -> None:
        self.username_service = username_service or UsernameService()

    def create_user(self, email: str, password_hash: str, username: str | None = None) -> dict:
        key = email.lower()
        if self.get_by_email(key):
            raise ValidationError("Email already registered", error_code=error_codes.DUPLICATE_RESOURCE_ERROR)

        normalized_username = None
        if username:
            normalized_username, error = self.username_service.validate(username)
            if error:
                raise ValidationError(error)
            availability = self.username_service.availability(normalized_username)
            if not availability["available"]:
                raise ValidationError("Username is not available", error_code=error_codes.DUPLICATE_RESOURCE_ERROR)

        default_plan = Plan.query.filter_by(code="free", is_active=True).one_or_none()
        user = User(email=key, password_hash=password_hash, plan_id=default_plan.id if default_plan else None)
        db.session.add(user)
        db.session.flush()
        if normalized_username:
            db.session.add(UsernameReservation(username=normalized_username, user_id=user.id, reason="registration"))
            user.username = normalized_username
        db.session.commit()
        return self._to_dict(user)

    def get_by_email(self, email: str) -> dict | None:
        user = User.query.filter_by(email=email.lower()).one_or_none()
        return self._to_dict(user) if user else None

    def get_model_by_email(self, email: str) -> User | None:
        return User.query.filter_by(email=email.lower()).one_or_none()

    def get_by_id(self, user_id: str) -> dict | None:
        user = User.query.filter_by(id=user_id).one_or_none()
        return self._to_dict(user) if user else None

    def get_model_by_id(self, user_id: str) -> User | None:
        return User.query.filter_by(id=user_id).one_or_none()

    def update_password(self, user: User, password_hash: str) -> dict:
        user.password_hash = password_hash
        user.token_version = int(user.token_version or 0) + 1
        db.session.commit()
        return self._to_dict(user)

    def mark_email_verified(self, user: User) -> dict:
        user.is_email_verified = True
        db.session.commit()
        return self._to_dict(user)

    def _to_dict(self, user: User) -> dict:
        plan_code = None
        if user.plan_id:
            plan = Plan.query.filter_by(id=user.plan_id).one_or_none()
            plan_code = plan.code if plan else None
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "password_hash": user.password_hash,
            "role": user.role,
            "is_active": user.is_active,
            "is_email_verified": user.is_email_verified,
            "plan_id": user.plan_id,
            "plan_code": plan_code,
            "subscription_status": user.subscription_status,
            "subscription_started_at": user.subscription_started_at,
            "subscription_expires_at": user.subscription_expires_at,
            "token_version": user.token_version,
        }
