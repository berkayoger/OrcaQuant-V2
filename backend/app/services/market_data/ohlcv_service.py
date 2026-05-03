from __future__ import annotations

from app.core.errors.exceptions import NotFoundError
from app.repositories.asset_repository import AssetRepository
from app.repositories.market_data_repository import MarketDataRepository
from app.services.market_data.sample_provider import SampleMarketDataProvider


class OhlcvService:
    def __init__(
        self,
        asset_repository: AssetRepository | None = None,
        market_data_repository: MarketDataRepository | None = None,
        provider: SampleMarketDataProvider | None = None,
    ) -> None:
        self.asset_repository = asset_repository or AssetRepository()
        self.market_data_repository = market_data_repository or MarketDataRepository()
        self.provider = provider or SampleMarketDataProvider()

    def sync_ohlcv(self, symbol: str, timeframe: str = "1d", limit: int = 200) -> dict:
        asset = self.asset_repository.get_by_symbol(symbol)
        if not asset:
            raise NotFoundError(f"Asset not found: {symbol}")

        rows = self.provider.get_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)
        count = self.market_data_repository.upsert_ohlcv(
            asset_id=asset["id"],
            rows=rows,
            source="sample",
            timeframe=timeframe,
        )
        return {"asset": asset["symbol"], "timeframe": timeframe, "rows_written": count}

    def get_ohlcv(self, symbol: str, timeframe: str = "1d", limit: int = 200) -> list[dict]:
        asset = self.asset_repository.get_by_symbol(symbol)
        if not asset:
            raise NotFoundError(f"Asset not found: {symbol}")

        rows = self.market_data_repository.get_ohlcv(asset["id"], timeframe=timeframe, limit=limit)
        if not rows:
            self.sync_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)
            rows = self.market_data_repository.get_ohlcv(asset["id"], timeframe=timeframe, limit=limit)
        return rows
