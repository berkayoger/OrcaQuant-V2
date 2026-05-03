from app.services.assets.asset_service import AssetService
from app.services.market_data.ohlcv_service import OhlcvService
from app.services.market_data.sample_provider import SampleMarketDataProvider


def test_ohlcv_service_sync_and_get(app):
    with app.app_context():
        AssetService().sync_assets_from_provider(SampleMarketDataProvider())
        svc = OhlcvService()
        result = svc.sync_ohlcv("BTC", limit=10)
        rows = svc.get_ohlcv("BTC", limit=10)
        assert result["rows_written"] == 10
        assert len(rows) == 10
