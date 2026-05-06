from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class DecisionResult(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "decision_results"

    asset_id = db.Column(db.String(36), db.ForeignKey("assets.id"), nullable=False, index=True)
    analysis_id = db.Column(db.String(36), db.ForeignKey("analysis_results.id"), nullable=True, index=True)
    payload_json = db.Column(db.JSON, nullable=False)
