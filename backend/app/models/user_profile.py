from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class UserProfile(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "user_profiles"
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, unique=True)

    display_name = db.Column(db.String(120), nullable=True)
    bio = db.Column(db.String(280), nullable=True)
    avatar_url = db.Column(db.String(512), nullable=True)

    risk_profile = db.Column(db.String(32), nullable=False, default="BALANCED")
    preferred_horizon_days = db.Column(db.Integer, nullable=False, default=30)
    max_drawdown_tolerance = db.Column(db.Float, nullable=False, default=0.20)
    capital = db.Column(db.Numeric(18, 2), nullable=True)

    preferred_currency = db.Column(db.String(8), nullable=False, default="USD")
    locale = db.Column(db.String(16), nullable=False, default="tr-TR")
    timezone = db.Column(db.String(64), nullable=False, default="Europe/Istanbul")
    theme = db.Column(db.String(16), nullable=False, default="system")

    notification_preferences = db.Column(db.JSON, nullable=False, default=dict)
    onboarding = db.Column(db.JSON, nullable=False, default=dict)
    privacy = db.Column(db.JSON, nullable=False, default=dict)
