from app.extensions import db
from app.models.base import TimestampMixin, UUIDPrimaryKeyMixin


class MarketPrice(UUIDPrimaryKeyMixin, TimestampMixin, db.Model):
    __tablename__ = "market_prices"
    __table_args__ = (
        db.UniqueConstraint(
            "asset_id",
            "timestamp",
            "timeframe",
            "source",
            name="uq_market_prices_asset_timestamp_timeframe_source",
        ),
    )

    asset_id = db.Column(db.String(36), db.ForeignKey("assets.id"), nullable=False, index=True)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    timeframe = db.Column(db.String(16), nullable=False, default="1d", index=True)
    open = db.Column(db.Float, nullable=False)
    high = db.Column(db.Float, nullable=False)
    low = db.Column(db.Float, nullable=False)
    close = db.Column(db.Float, nullable=False)
    volume = db.Column(db.Float, nullable=False, default=0.0)
    source = db.Column(db.String(64), nullable=False, default="manual")
