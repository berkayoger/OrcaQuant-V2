from __future__ import annotations

from typing import Protocol


class AssetProviderProtocol(Protocol):
    def list_assets(self) -> list[dict]: ...


class OhlcvProviderProtocol(Protocol):
    def get_ohlcv(self, symbol: str, timeframe: str = "1d", limit: int = 200) -> list[dict]: ...


class MarketDataProviderProtocol(AssetProviderProtocol, OhlcvProviderProtocol, Protocol): ...
