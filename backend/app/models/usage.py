from datetime import date
from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class FeatureLimit(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "feature_limits"
    plan_id = db.Column(db.String(36), db.ForeignKey("plans.id"), nullable=False, index=True)
    feature_key = db.Column(db.String(64), nullable=False, index=True)
    daily_quota = db.Column(db.Integer, nullable=True)
    monthly_quota = db.Column(db.Integer, nullable=True)
    enabled = db.Column(db.Boolean, nullable=False, default=True)


class DailyUsage(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "daily_usage"
    __table_args__ = (
        db.UniqueConstraint("user_id", "feature_key", "usage_date", name="uq_daily_usage_user_feature_date"),
    )
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    feature_key = db.Column(db.String(64), nullable=False, index=True)
    usage_date = db.Column(db.Date, nullable=False, index=True, default=date.today)
    used_count = db.Column(db.Integer, nullable=False, default=0)
