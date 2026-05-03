from app.extensions import db
from app.models.base import UUIDPrimaryKeyMixin


class LimitPolicy(UUIDPrimaryKeyMixin, db.Model):
    __tablename__ = "limit_policies"
    plan_id = db.Column(db.String(36), db.ForeignKey("plans.id"), nullable=False, index=True)
    feature = db.Column(db.String(100), nullable=False)
    daily_limit = db.Column(db.Integer, nullable=True)
    monthly_limit = db.Column(db.Integer, nullable=True)
