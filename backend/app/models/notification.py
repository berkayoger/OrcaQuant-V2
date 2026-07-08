from datetime import UTC, datetime

from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Notification(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "notifications"

    user_id = db.Column(db.String(36), nullable=False, index=True)
    type = db.Column(db.String(64), nullable=False, default="alert", index=True)
    status = db.Column(db.String(32), nullable=False, default="unread", index=True)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text, nullable=True)
    source_event_key = db.Column(db.String(255), nullable=True, unique=True, index=True)
    data = db.Column(db.JSON, nullable=True)
    read_at = db.Column(db.DateTime(timezone=True), nullable=True)

    def mark_read(self) -> None:
        if self.status != "read":
            self.status = "read"
            self.read_at = datetime.now(UTC)
