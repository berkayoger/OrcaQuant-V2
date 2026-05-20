from app.services.market_data.coingecko_provider import CoinGeckoMarketDataProvider
from app.services.market_data.provider_factory import get_market_data_provider
from app.services.market_data.sample_provider import SampleMarketDataProvider


def test_provider_factory_sample_default(app):
    with app.app_context():
        app.config["MARKET_DATA_PROVIDER"] = "sample"
        provider = get_market_data_provider()
        assert isinstance(provider, SampleMarketDataProvider)


def test_provider_factory_coingecko(app):
    with app.app_context():
        app.config["MARKET_DATA_PROVIDER"] = "coingecko"
        app.config["MARKET_DATA_TIMEOUT_SECONDS"] = 5
        app.config["MARKET_DATA_CACHE_TTL_SECONDS"] = 99
        provider = get_market_data_provider()
        assert isinstance(provider, CoinGeckoMarketDataProvider)
        assert provider.timeout_seconds == 5
        assert provider.cache_ttl_seconds == 99
