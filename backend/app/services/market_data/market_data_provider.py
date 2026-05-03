from __future__ import annotations

from typing import Protocol


class MarketDataProvider(Protocol):
    def list_assets(self) -> list[dict]: ...

    def get_ohlcv(self, symbol: str, timeframe: str = "1d", limit: int = 200) -> list[dict]: ...
