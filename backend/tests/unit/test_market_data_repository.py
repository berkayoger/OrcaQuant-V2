from datetime import UTC, datetime

from app.repositories.asset_repository import AssetRepository
from app.repositories.market_data_repository import MarketDataRepository


def test_ohlcv_upsert_and_order(app):
    with app.app_context():
        asset = AssetRepository().create_asset("BTC", "Bitcoin")
        repo = MarketDataRepository()
        ts = datetime(2024, 1, 1, tzinfo=UTC)
        rows = [{"timestamp": ts, "open": 1, "high": 2, "low": 0.5, "close": 1.5, "volume": 10}]
        repo.upsert_ohlcv(asset["id"], rows, source="sample")
        repo.upsert_ohlcv(asset["id"], [{**rows[0], "close": 9}], source="sample")
        out = repo.get_ohlcv(asset["id"])
        assert len(out) == 1
        assert out[0]["close"] == 9
