from __future__ import annotations

from app.extensions import db
from app.models.market_price import MarketPrice


class MarketDataRepository:
    def upsert_ohlcv(self, asset_id: str, rows: list[dict], source: str = "manual", timeframe: str = "1d") -> int:
        written = 0
        for row in rows:
            existing = MarketPrice.query.filter_by(
                asset_id=asset_id,
                timestamp=row["timestamp"],
                timeframe=timeframe,
                source=source,
            ).one_or_none()
            if existing:
                existing.open = float(row["open"])
                existing.high = float(row["high"])
                existing.low = float(row["low"])
                existing.close = float(row["close"])
                existing.volume = float(row.get("volume", 0))
            else:
                db.session.add(
                    MarketPrice(
                        asset_id=asset_id,
                        timestamp=row["timestamp"],
                        timeframe=timeframe,
                        source=source,
                        open=float(row["open"]),
                        high=float(row["high"]),
                        low=float(row["low"]),
                        close=float(row["close"]),
                        volume=float(row.get("volume", 0)),
                    )
                )
            written += 1
        db.session.commit()
        return written

    def get_ohlcv(self, asset_id: str, timeframe: str = "1d", limit: int = 200) -> list[dict]:
        rows = (
            MarketPrice.query.filter_by(asset_id=asset_id, timeframe=timeframe)
            .order_by(MarketPrice.timestamp.asc())
            .limit(limit)
            .all()
        )
        return [self._to_dict(row) for row in rows]

    def get_latest_price(self, asset_id: str, timeframe: str = "1d") -> dict | None:
        row = (
            MarketPrice.query.filter_by(asset_id=asset_id, timeframe=timeframe)
            .order_by(MarketPrice.timestamp.desc())
            .first()
        )
        return self._to_dict(row) if row else None

    def _to_dict(self, row: MarketPrice) -> dict:
        return {
            "id": row.id,
            "asset_id": row.asset_id,
            "timestamp": row.timestamp.isoformat(),
            "timeframe": row.timeframe,
            "open": row.open,
            "high": row.high,
            "low": row.low,
            "close": row.close,
            "volume": row.volume,
            "source": row.source,
        }
