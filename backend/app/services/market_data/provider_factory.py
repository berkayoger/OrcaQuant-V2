from __future__ import annotations

from flask import current_app

from app.services.market_data.coingecko_provider import CoinGeckoMarketDataProvider
from app.services.market_data.provider_protocol import MarketDataProviderProtocol
from app.services.market_data.sample_provider import SampleMarketDataProvider


def get_market_data_provider() -> MarketDataProviderProtocol:
    provider_name = current_app.config.get("MARKET_DATA_PROVIDER", "sample").lower()
    timeout = int(current_app.config.get("MARKET_DATA_TIMEOUT_SECONDS", 10))
    ttl = int(current_app.config.get("MARKET_DATA_CACHE_TTL_SECONDS", 300))

    if provider_name == "coingecko":
        return CoinGeckoMarketDataProvider(timeout_seconds=timeout, cache_ttl_seconds=ttl)
    if provider_name == "binance":
        # temporary fallback until dedicated Binance provider is added.
        return SampleMarketDataProvider()
    return SampleMarketDataProvider()
