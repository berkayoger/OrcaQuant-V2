from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class Asset(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "assets"

    symbol = db.Column(db.String(32), unique=True, index=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    asset_type = db.Column(db.String(64), nullable=False, default="crypto")
    provider = db.Column(db.String(64), nullable=False, default="manual")
    provider_id = db.Column(db.String(128), nullable=True, index=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    metadata_json = db.Column(db.JSON, nullable=True)
