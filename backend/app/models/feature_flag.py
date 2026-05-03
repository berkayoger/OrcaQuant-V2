from app.extensions import db
from app.models.base import UUIDPrimaryKeyMixin


class FeatureFlag(UUIDPrimaryKeyMixin, db.Model):
    __tablename__ = "feature_flags"
    key = db.Column(db.String(120), unique=True, nullable=False)
    enabled = db.Column(db.Boolean, nullable=False, default=False)
    description = db.Column(db.Text, nullable=True)
