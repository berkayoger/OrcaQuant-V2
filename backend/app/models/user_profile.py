from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class UserProfile(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "user_profiles"
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, unique=True)
    risk_profile = db.Column(db.String(32), nullable=False, default="BALANCED")
    preferred_horizon_days = db.Column(db.Integer, nullable=False, default=30)
    max_drawdown_tolerance = db.Column(db.Float, nullable=False, default=0.20)
    capital = db.Column(db.Numeric(18, 2), nullable=True)
