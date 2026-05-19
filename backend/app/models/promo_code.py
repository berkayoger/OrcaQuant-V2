from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class PromoCode(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "promo_codes"
    code = db.Column(db.String(64), unique=True, nullable=False, index=True)
    plan_code = db.Column(db.String(32), nullable=False)
    max_uses = db.Column(db.Integer, nullable=True)
    current_uses = db.Column(db.Integer, nullable=False, default=0)
    duration_days = db.Column(db.Integer, nullable=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    single_use_per_user = db.Column(db.Boolean, nullable=False, default=True)
