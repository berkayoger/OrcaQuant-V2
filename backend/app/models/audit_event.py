from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class AuditEvent(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "audit_events"
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=True, index=True)
    event_type = db.Column(db.String(64), nullable=False)
    action = db.Column(db.String(64), nullable=False)
    target = db.Column(db.String(128), nullable=True)
    status = db.Column(db.String(32), nullable=False, default="ok")
    ip_address = db.Column(db.String(64), nullable=True)
    user_agent = db.Column(db.String(512), nullable=True)
    metadata_json = db.Column(db.Text, nullable=True)
