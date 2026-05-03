from app.extensions import db
from app.models.base import UUIDPrimaryKeyMixin
from datetime import UTC, datetime


class ApiKey(UUIDPrimaryKeyMixin, db.Model):
    __tablename__ = "api_keys"
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    key_hash = db.Column(db.String(255), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
    revoked_at = db.Column(db.DateTime(timezone=True), nullable=True)
