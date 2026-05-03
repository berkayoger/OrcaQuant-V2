from app.extensions import db
from app.models.base import UUIDPrimaryKeyMixin
from datetime import UTC, datetime


class PaymentEvent(UUIDPrimaryKeyMixin, db.Model):
    __tablename__ = "payment_events"
    provider = db.Column(db.String(50), nullable=False)
    event_id = db.Column(db.String(120), unique=True, nullable=False)
    event_type = db.Column(db.String(120), nullable=False)
    payload_json = db.Column(db.JSON, nullable=False)
    processed_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
