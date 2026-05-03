from __future__ import annotations

from app.core.errors.exceptions import NotFoundError
from app.core.engines.technical_signal_engine import TechnicalSignalEngine
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.asset_repository import AssetRepository
from app.repositories.market_data_repository import MarketDataRepository
from app.services.market_data.ohlcv_service import OhlcvService


class AssetAnalysisService:
    def __init__(
        self,
        asset_repository: AssetRepository | None = None,
        market_data_repository: MarketDataRepository | None = None,
        ohlcv_service: OhlcvService | None = None,
        technical_signal_engine: TechnicalSignalEngine | None = None,
        analysis_repository: AnalysisRepository | None = None,
    ) -> None:
        self.asset_repository = asset_repository or AssetRepository()
        self.market_data_repository = market_data_repository or MarketDataRepository()
        self.ohlcv_service = ohlcv_service or OhlcvService(
            asset_repository=self.asset_repository,
            market_data_repository=self.market_data_repository,
        )
        self.technical_signal_engine = technical_signal_engine or TechnicalSignalEngine()
        self.analysis_repository = analysis_repository or AnalysisRepository()

    def run_technical_analysis(self, symbol: str, timeframe: str = "1d", limit: int = 200) -> dict:
        asset = self.asset_repository.get_by_symbol(symbol)
        if not asset:
            raise NotFoundError(f"Asset not found: {symbol}")

        rows = self.market_data_repository.get_ohlcv(asset["id"], timeframe=timeframe, limit=limit)
        if not rows:
            self.ohlcv_service.sync_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)
            rows = self.market_data_repository.get_ohlcv(asset["id"], timeframe=timeframe, limit=limit)

        result = self.technical_signal_engine.run(rows)
        saved = self.analysis_repository.create_analysis_result(
            asset_id=asset["id"],
            analysis_type="technical",
            payload=result.to_dict(),
        )

        return {
            "symbol": asset["symbol"],
            "timeframe": timeframe,
            "analysis_type": "technical",
            "result": result.to_dict(),
            "saved_analysis_id": saved["id"],
        }

    def get_latest_analysis(self, symbol: str, analysis_type: str = "technical") -> dict | None:
        asset = self.asset_repository.get_by_symbol(symbol)
        if not asset:
            raise NotFoundError(f"Asset not found: {symbol}")

        latest = self.analysis_repository.get_latest_for_asset(asset["id"], analysis_type=analysis_type)
        if not latest:
            return None

        return {
            "symbol": asset["symbol"],
            "analysis_type": analysis_type,
            "analysis": latest,
        }
