from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class PaymentTransaction(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "payment_transactions"
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    provider = db.Column(db.String(32), nullable=False)
    provider_payment_id = db.Column(db.String(128), nullable=True)
    provider_conversation_id = db.Column(db.String(128), nullable=True)
    plan_code = db.Column(db.String(32), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(8), nullable=False, default="TRY")
    status = db.Column(db.String(32), nullable=False, default="pending")
    raw_payload_json = db.Column(db.Text, nullable=True)
