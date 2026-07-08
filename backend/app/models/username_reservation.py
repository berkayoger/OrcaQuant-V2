from datetime import UTC, datetime

from app.extensions import db
from app.models.base import UUIDPrimaryKeyMixin


class UsernameReservation(UUIDPrimaryKeyMixin, db.Model):
    __tablename__ = "username_reservations"

    username = db.Column(db.String(32), unique=True, nullable=False, index=True)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    reason = db.Column(db.String(40), nullable=False, default="claimed")
    reserved_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC))
