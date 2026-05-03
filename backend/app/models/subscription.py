from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Subscription(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "subscriptions"
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    plan_id = db.Column(db.String(36), db.ForeignKey("plans.id"), nullable=False, index=True)
    status = db.Column(db.String(30), nullable=False, default="active")
    current_period_start = db.Column(db.DateTime(timezone=True), nullable=True)
    current_period_end = db.Column(db.DateTime(timezone=True), nullable=True)
