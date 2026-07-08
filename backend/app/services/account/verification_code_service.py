from __future__ import annotations

from datetime import UTC, datetime, timedelta
from hashlib import sha256
import secrets

from flask import current_app

from app.core.errors.exceptions import AuthenticationError, ValidationError
from app.extensions import db
from app.models.account_verification_code import AccountVerificationCode
from app.models.user import User
from app.services.account.verification_delivery_service import VerificationDeliveryService


class AccountVerificationCodeService:
    PURPOSE_EMAIL_VERIFICATION = "email_verification"
    PURPOSE_LOGIN = "login"
    PURPOSE_PASSWORD_RESET = "password_reset"
    PURPOSES = {PURPOSE_EMAIL_VERIFICATION, PURPOSE_LOGIN, PURPOSE_PASSWORD_RESET}

    def __init__(self, delivery_service: VerificationDeliveryService | None = None) -> None:
        self.delivery_service = delivery_service or VerificationDeliveryService()

    def send_code(self, *, email: str, purpose: str, expose_missing_user: bool = True) -> dict:
        clean_email = self._normalize_email(email)
        clean_purpose = str(purpose or "").strip().lower()
        if clean_purpose not in self.PURPOSES:
            raise ValidationError(f"purpose must be one of {sorted(self.PURPOSES)}")

        user = User.query.filter_by(email=clean_email).one_or_none()
        if not user:
            if expose_missing_user:
                raise AuthenticationError("Account not found")
            return {"sent": True, "status": "sent_if_account_exists", "purpose": clean_purpose}

        code = self._new_code()
        self._invalidate_pending_codes(clean_email, clean_purpose)
        row = AccountVerificationCode(
            user_id=user.id,
            email=clean_email,
            purpose=clean_purpose,
            code_hash=self._hash_code(clean_email, clean_purpose, code),
            expires_at=datetime.now(UTC) + timedelta(minutes=self._ttl_minutes()),
            max_attempts=self._max_attempts(),
            delivery_channel=str(current_app.config.get("ACCOUNT_CODE_CHANNEL", "email")),
            delivery_status="queued",
            metadata={"requested_at": datetime.now(UTC).isoformat()},
        )
        db.session.add(row)
        db.session.flush()
        delivery = self.delivery_service.deliver(email=clean_email, code=code, purpose=clean_purpose)
        row.delivery_status = delivery.get("status", "queued")
        db.session.commit()
        return {
            "sent": True,
            "status": row.delivery_status,
            "purpose": clean_purpose,
            "expires_in_minutes": self._ttl_minutes(),
            "delivery": delivery,
        }

    def verify_code(self, *, email: str, purpose: str, code: str, consume: bool = True) -> User:
        clean_email = self._normalize_email(email)
        clean_purpose = str(purpose or "").strip().lower()
        if clean_purpose not in self.PURPOSES:
            raise ValidationError(f"purpose must be one of {sorted(self.PURPOSES)}")
        clean_code = str(code or "").strip()
        if not clean_code:
            raise ValidationError("code is required")

        row = (
            AccountVerificationCode.query.filter_by(email=clean_email, purpose=clean_purpose, status="pending")
            .order_by(AccountVerificationCode.created_at.desc())
            .first()
        )
        if not row:
            raise AuthenticationError("Invalid or expired verification code")
        if row.is_expired():
            row.status = "expired"
            db.session.commit()
            raise AuthenticationError("Verification code expired")
        if row.code_hash != self._hash_code(clean_email, clean_purpose, clean_code):
            row.fail_attempt()
            db.session.commit()
            raise AuthenticationError("Invalid verification code")

        user = db.session.get(User, row.user_id) if row.user_id else User.query.filter_by(email=clean_email).one_or_none()
        if not user or not user.is_active:
            row.status = "invalid_user"
            db.session.commit()
            raise AuthenticationError("Invalid user")

        if consume:
            row.consume()
            db.session.commit()
        return user

    def _invalidate_pending_codes(self, email: str, purpose: str) -> None:
        rows = AccountVerificationCode.query.filter_by(email=email, purpose=purpose, status="pending").all()
        for row in rows:
            row.status = "superseded"

    def _hash_code(self, email: str, purpose: str, code: str) -> str:
        secret = str(current_app.config.get("SECRET_KEY") or "dev-secret")
        value = f"{secret}:{email}:{purpose}:{code}"
        return sha256(value.encode("utf-8")).hexdigest()

    @staticmethod
    def _normalize_email(email: str) -> str:
        clean = str(email or "").strip().lower()
        if "@" not in clean:
            raise ValidationError("valid email is required")
        return clean

    @staticmethod
    def _new_code() -> str:
        return f"{secrets.randbelow(1_000_000):06d}"

    @staticmethod
    def _ttl_minutes() -> int:
        return int(current_app.config.get("ACCOUNT_VERIFICATION_CODE_TTL_MINUTES", 10))

    @staticmethod
    def _max_attempts() -> int:
        return int(current_app.config.get("ACCOUNT_VERIFICATION_MAX_ATTEMPTS", 5))
