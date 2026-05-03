from app.services.market_data.sample_provider import SampleMarketDataProvider


def test_provider_assets_and_determinism():
    provider = SampleMarketDataProvider()
    symbols = [x["symbol"] for x in provider.list_assets()]
    assert symbols == ["BTC", "ETH", "SOL", "AVAX", "XRP"]
    rows1 = provider.get_ohlcv("BTC", limit=5)
    rows2 = provider.get_ohlcv("BTC", limit=5)
    assert rows1 == rows2
