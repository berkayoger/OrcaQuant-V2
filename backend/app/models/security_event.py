from app.extensions import db
from app.models.base import UUIDPrimaryKeyMixin
from datetime import UTC, datetime


class SecurityEvent(UUIDPrimaryKeyMixin, db.Model):
    __tablename__ = "security_events"
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True, index=True)
    event_type = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(64), nullable=True)
    user_agent = db.Column(db.String(512), nullable=True)
    metadata_json = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
