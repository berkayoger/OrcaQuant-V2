from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Permission(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "permissions"
    key = db.Column(db.String(100), unique=True, nullable=False)
