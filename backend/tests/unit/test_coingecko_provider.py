from app.services.market_data.coingecko_provider import CoinGeckoMarketDataProvider
from app.services.market_data.exceptions import MarketDataProviderError


class StubProvider(CoinGeckoMarketDataProvider):
    def __init__(self):
        super().__init__(timeout_seconds=1, cache_ttl_seconds=60)
        self.calls = 0

    def _fetch_json_with_retry(self, url: str):
        self.calls += 1
        return [
            [1710000000000, 100.0, 110.0, 90.0, 105.0],
            [1710086400000, 105.0, 120.0, 100.0, 118.0],
        ]


def test_coingecko_ohlcv_and_cache():
    provider = StubProvider()
    rows1 = provider.get_ohlcv("BTC", limit=2)
    rows2 = provider.get_ohlcv("BTC", limit=2)
    assert len(rows1) == 2
    assert rows1 == rows2
    assert provider.calls == 1


def test_coingecko_rejects_unsupported_symbol():
    provider = CoinGeckoMarketDataProvider()
    try:
        provider.get_ohlcv("DOGE")
    except MarketDataProviderError as exc:
        assert "Symbol not supported" in str(exc)
    else:
        raise AssertionError("expected MarketDataProviderError")
