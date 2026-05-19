from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Session(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "sessions"
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    refresh_token_hash = db.Column(db.String(255), nullable=False, index=True)
    jti = db.Column(db.String(64), nullable=False, unique=True, index=True)
    user_agent = db.Column(db.String(512), nullable=True)
    ip_address = db.Column(db.String(64), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    revoked_at = db.Column(db.DateTime(timezone=True), nullable=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
