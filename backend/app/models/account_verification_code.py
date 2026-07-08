from datetime import UTC, datetime

from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class AccountVerificationCode(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "account_verification_codes"

    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True, index=True)
    email = db.Column(db.String(255), nullable=False, index=True)
    purpose = db.Column(db.String(40), nullable=False, index=True)
    code_hash = db.Column(db.String(128), nullable=False)
    status = db.Column(db.String(32), nullable=False, default="pending", index=True)
    attempts = db.Column(db.Integer, nullable=False, default=0)
    max_attempts = db.Column(db.Integer, nullable=False, default=5)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    consumed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    delivery_channel = db.Column(db.String(32), nullable=False, default="email")
    delivery_status = db.Column(db.String(32), nullable=False, default="queued")
    metadata = db.Column(db.JSON, nullable=True)

    def is_expired(self) -> bool:
        now = datetime.now(UTC)
        expires_at = self.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        return now >= expires_at

    def consume(self) -> None:
        self.status = "consumed"
        self.consumed_at = datetime.now(UTC)

    def fail_attempt(self) -> None:
        self.attempts += 1
        if self.attempts >= self.max_attempts:
            self.status = "locked"
