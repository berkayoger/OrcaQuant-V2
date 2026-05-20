from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from app.services.market_data.exceptions import MarketDataProviderError


class CoinGeckoMarketDataProvider:
    provider_name = "coingecko"
    BASE_URL = "https://api.coingecko.com/api/v3"
    MAX_RETRIES = 3
    RETRY_BASE_SECONDS = 0.3

    _SYMBOL_TO_ID = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
        "AVAX": "avalanche-2",
        "XRP": "ripple",
    }

    def __init__(self, timeout_seconds: int = 10, cache_ttl_seconds: int = 300) -> None:
        self.timeout_seconds = timeout_seconds
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cache: dict[str, tuple[float, list[dict]]] = {}

    def list_assets(self) -> list[dict]:
        return [
            {"symbol": symbol, "name": asset_id.replace("-", " ").title(), "asset_type": "crypto", "provider": "coingecko", "provider_id": asset_id}
            for symbol, asset_id in self._SYMBOL_TO_ID.items()
        ]

    def get_ohlcv(self, symbol: str, timeframe: str = "1d", limit: int = 200) -> list[dict]:
        if timeframe != "1d":
            raise MarketDataProviderError("CoinGecko provider currently supports only 1d timeframe")

        cache_key = f"{symbol.upper()}:{timeframe}:{limit}"
        cached = self._cache.get(cache_key)
        now = time.time()
        if cached and now - cached[0] <= self.cache_ttl_seconds:
            return cached[1]

        asset_id = self._SYMBOL_TO_ID.get(symbol.upper())
        if not asset_id:
            raise MarketDataProviderError(f"Symbol not supported by CoinGecko provider: {symbol}")

        params = urlencode({"vs_currency": "usd", "days": str(limit), "interval": "daily"})
        url = f"{self.BASE_URL}/coins/{asset_id}/ohlc?{params}"
        payload = self._fetch_json_with_retry(url)

        rows = [
            {
                "timestamp": datetime.fromtimestamp(entry[0] / 1000, tz=UTC),
                "open": float(entry[1]),
                "high": float(entry[2]),
                "low": float(entry[3]),
                "close": float(entry[4]),
                "volume": 0.0,
            }
            for entry in payload[-limit:]
        ]
        self._cache[cache_key] = (now, rows)
        return rows

    def _fetch_json_with_retry(self, url: str):
        last_error: Exception | None = None
        for attempt in range(self.MAX_RETRIES):
            try:
                with urlopen(url, timeout=self.timeout_seconds) as response:  # noqa: S310
                    return json.loads(response.read().decode("utf-8"))
            except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
                last_error = exc
                if attempt == self.MAX_RETRIES - 1:
                    break
                time.sleep(self.RETRY_BASE_SECONDS * (2**attempt))

        raise MarketDataProviderError(f"CoinGecko request failed after retries: {last_error}")
