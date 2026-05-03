from __future__ import annotations

from datetime import UTC, datetime, timedelta
from random import Random


class SampleMarketDataProvider:
    _ASSETS = [
        {"symbol": "BTC", "name": "Bitcoin", "asset_type": "crypto"},
        {"symbol": "ETH", "name": "Ethereum", "asset_type": "crypto"},
        {"symbol": "SOL", "name": "Solana", "asset_type": "crypto"},
        {"symbol": "AVAX", "name": "Avalanche", "asset_type": "crypto"},
        {"symbol": "XRP", "name": "XRP", "asset_type": "crypto"},
    ]

    def list_assets(self) -> list[dict]:
        return [dict(asset) for asset in self._ASSETS]

    def get_ohlcv(self, symbol: str, timeframe: str = "1d", limit: int = 200) -> list[dict]:
        seed = f"{symbol.upper()}:{timeframe}:{limit}"
        rng = Random(seed)
        base_price = 10 + (sum(ord(char) for char in symbol.upper()) % 200)
        end = datetime(2025, 1, 1, tzinfo=UTC)
        rows: list[dict] = []
        for idx in range(limit):
            ts = end - timedelta(days=limit - idx)
            drift = idx * 0.35
            open_price = base_price + drift + rng.uniform(-1.2, 1.2)
            close_price = open_price + rng.uniform(-2.0, 2.0)
            high_price = max(open_price, close_price) + rng.uniform(0.1, 1.8)
            low_price = min(open_price, close_price) - rng.uniform(0.1, 1.8)
            rows.append(
                {
                    "timestamp": ts,
                    "open": round(open_price, 4),
                    "high": round(high_price, 4),
                    "low": round(low_price, 4),
                    "close": round(close_price, 4),
                    "volume": round(1000 + rng.uniform(10, 8000) + idx * 5, 4),
                }
            )
        return rows
