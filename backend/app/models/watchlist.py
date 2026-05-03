from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Watchlist(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "watchlists"
    user_id = db.Column(db.String(36), nullable=True, index=True)
    data = db.Column(db.JSON, nullable=True)
