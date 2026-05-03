from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Plan(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "plans"
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price_monthly_cents = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
