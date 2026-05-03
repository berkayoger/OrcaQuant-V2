from app.extensions import db
from app.models.base import UUIDPrimaryKeyMixin
from datetime import UTC, datetime


class Invoice(UUIDPrimaryKeyMixin, db.Model):
    __tablename__ = "invoices"
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    subscription_id = db.Column(db.String(36), db.ForeignKey("subscriptions.id"), nullable=True, index=True)
    amount_cents = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="USD")
    status = db.Column(db.String(30), nullable=False, default="pending")
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
