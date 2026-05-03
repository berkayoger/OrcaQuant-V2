from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class User(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "users"

    email = db.Column(db.String(255), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="user")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_email_verified = db.Column(db.Boolean, nullable=False, default=False)
