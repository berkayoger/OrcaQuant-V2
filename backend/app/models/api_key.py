from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class ApiKey(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "api_keys"
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    key_hash = db.Column(db.String(255), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    last_used_at = db.Column(db.DateTime(timezone=True), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
