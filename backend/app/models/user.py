from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class User(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "users"

    email = db.Column(db.String(255), unique=True, index=True, nullable=False)
    username = db.Column(db.String(32), unique=True, index=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_email_verified = db.Column(db.Boolean, nullable=False, default=False)
    plan_id = db.Column(db.String(36), db.ForeignKey("plans.id"), nullable=True, index=True)
    subscription_status = db.Column(db.String(50), nullable=False, default="free")
    subscription_started_at = db.Column(db.DateTime(timezone=True), nullable=True)
    subscription_expires_at = db.Column(db.DateTime(timezone=True), nullable=True)
    token_version = db.Column(db.Integer, nullable=False, default=0)
