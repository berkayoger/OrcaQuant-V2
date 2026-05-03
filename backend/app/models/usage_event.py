from app.extensions import db
from app.models.base import UUIDPrimaryKeyMixin
from datetime import UTC, date, datetime


class UsageEvent(UUIDPrimaryKeyMixin, db.Model):
    __tablename__ = "usage_events"
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    feature = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, nullable=False, default=1)
    usage_date = db.Column(db.Date, nullable=False, default=date.today)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
