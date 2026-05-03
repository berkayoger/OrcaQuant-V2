from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class AnalysisResult(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "analysis_results"

    asset_id = db.Column(db.String(36), db.ForeignKey("assets.id"), nullable=False, index=True)
    analysis_type = db.Column(db.String(64), nullable=False, default="technical", index=True)
    payload_json = db.Column(db.JSON, nullable=False)
