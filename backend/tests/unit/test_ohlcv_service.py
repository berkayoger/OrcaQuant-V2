from app.services.assets.asset_service import AssetService
from app.services.market_data.ohlcv_service import OhlcvService
from app.services.market_data.exceptions import MarketDataProviderError
from app.services.market_data.sample_provider import SampleMarketDataProvider


def test_ohlcv_service_sync_and_get(app):
    with app.app_context():
        AssetService().sync_assets_from_provider(SampleMarketDataProvider())
        svc = OhlcvService()
        result = svc.sync_ohlcv("BTC", limit=10)
        rows = svc.get_ohlcv("BTC", limit=10)
        assert result["rows_written"] == 10
        assert len(rows) == 10


class BrokenProvider:
    def get_ohlcv(self, symbol: str, timeframe: str = "1d", limit: int = 200) -> list[dict]:
        raise MarketDataProviderError("boom")


def test_ohlcv_service_falls_back_to_sample_when_provider_fails(app):
    with app.app_context():
        AssetService().sync_assets_from_provider(SampleMarketDataProvider())
        svc = OhlcvService(provider=BrokenProvider())
        result = svc.sync_ohlcv("BTC", limit=3)
        assert result["rows_written"] == 3
