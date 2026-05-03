from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class RefreshToken(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "refresh_tokens"
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    token_hash = db.Column(db.String(255), nullable=False, index=True)
    revoked_at = db.Column(db.DateTime(timezone=True), nullable=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
