from __future__ import annotations

from app.core.errors.exceptions import NotFoundError
from app.core.engines.final_consensus_engine import FinalConsensusEngine
from app.core.engines.monte_carlo_engine import MonteCarloEngine
from app.core.engines.risk_management_engine import RiskManagementEngine
from app.core.engines.schemas import ScenarioTarget
from app.core.engines.technical_signal_engine import TechnicalSignalEngine
from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.decision_repository import DecisionRepository
from app.repositories.asset_repository import AssetRepository
from app.repositories.monte_carlo_repository import MonteCarloRepository
from app.repositories.market_data_repository import MarketDataRepository
from app.repositories.risk_repository import RiskRepository
from app.services.market_data.ohlcv_service import OhlcvService


class AssetAnalysisService:
    def __init__(
        self,
        asset_repository: AssetRepository | None = None,
        market_data_repository: MarketDataRepository | None = None,
        ohlcv_service: OhlcvService | None = None,
        technical_signal_engine: TechnicalSignalEngine | None = None,
        analysis_repository: AnalysisRepository | None = None,
        monte_carlo_repository: MonteCarloRepository | None = None,
        risk_repository: RiskRepository | None = None,
        monte_carlo_engine: MonteCarloEngine | None = None,
        risk_management_engine: RiskManagementEngine | None = None,
        final_consensus_engine: FinalConsensusEngine | None = None,
        decision_repository: DecisionRepository | None = None,
    ) -> None:
        self.asset_repository = asset_repository or AssetRepository()
        self.market_data_repository = market_data_repository or MarketDataRepository()
        self.ohlcv_service = ohlcv_service or OhlcvService(
            asset_repository=self.asset_repository,
            market_data_repository=self.market_data_repository,
        )
        self.technical_signal_engine = technical_signal_engine or TechnicalSignalEngine()
        self.analysis_repository = analysis_repository or AnalysisRepository()
        self.monte_carlo_repository = monte_carlo_repository or MonteCarloRepository()
        self.risk_repository = risk_repository or RiskRepository()
        self.monte_carlo_engine = monte_carlo_engine or MonteCarloEngine()
        self.risk_management_engine = risk_management_engine or RiskManagementEngine()
        self.final_consensus_engine = final_consensus_engine or FinalConsensusEngine()
        self.decision_repository = decision_repository or DecisionRepository()

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

    def run_scenario_risk_analysis(self, symbol: str, timeframe: str = "1d", limit: int = 200, horizon_days: int = 14, targets: list[dict] | None = None) -> dict:
        asset = self.asset_repository.get_by_symbol(symbol)
        if not asset:
            raise NotFoundError(f"Asset not found: {symbol}")
        rows = self.market_data_repository.get_ohlcv(asset["id"], timeframe=timeframe, limit=limit)
        if not rows:
            self.ohlcv_service.sync_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)
            rows = self.market_data_repository.get_ohlcv(asset["id"], timeframe=timeframe, limit=limit)
        scenario_targets = [ScenarioTarget(name=t["name"], direction=t["direction"], price=float(t["price"])) for t in (targets or [])]
        mc = self.monte_carlo_engine.run(rows, horizon_days=horizon_days, targets=scenario_targets)
        risk = self.risk_management_engine.run(rows, mc)
        saved = self.analysis_repository.create_analysis_result(asset_id=asset["id"], analysis_type="scenario_risk", payload={"monte_carlo": mc.to_dict(), "risk": risk.to_dict()})
        self.monte_carlo_repository.create_result(asset_id=asset["id"], analysis_id=saved["id"], payload=mc.to_dict())
        self.risk_repository.create_result(asset_id=asset["id"], analysis_id=saved["id"], payload=risk.to_dict())
        return {"symbol": asset["symbol"], "timeframe": timeframe, "horizon_days": horizon_days, "analysis_type": "scenario_risk", "monte_carlo": mc.to_dict(), "risk": risk.to_dict(), "saved_analysis_id": saved["id"]}

    def run_full_analysis(
        self,
        symbol: str,
        timeframe: str = "1d",
        limit: int = 200,
        horizon_days: int = 14,
        targets: list[dict] | None = None,
    ) -> dict:
        asset = self.asset_repository.get_by_symbol(symbol)
        if not asset:
            raise NotFoundError(f"Asset not found: {symbol}")

        rows = self.market_data_repository.get_ohlcv(asset["id"], timeframe=timeframe, limit=limit)
        if not rows:
            self.ohlcv_service.sync_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)
            rows = self.market_data_repository.get_ohlcv(asset["id"], timeframe=timeframe, limit=limit)

        technical = self.technical_signal_engine.run(rows)
        scenario_targets = [
            ScenarioTarget(name=t["name"], direction=t["direction"], price=float(t["price"]))
            for t in (targets or [])
        ]
        monte_carlo = self.monte_carlo_engine.run(rows, horizon_days=horizon_days, targets=scenario_targets)
        risk = self.risk_management_engine.run(rows, monte_carlo)
        consensus = self.final_consensus_engine.run(technical, monte_carlo, risk)

        payload = {
            "technical": technical.to_dict(),
            "monte_carlo": monte_carlo.to_dict(),
            "risk": risk.to_dict(),
            "consensus": consensus.to_dict(),
        }
        saved = self.analysis_repository.create_analysis_result(
            asset_id=asset["id"],
            analysis_type="full",
            payload=payload,
        )
        self.monte_carlo_repository.create_result(asset_id=asset["id"], analysis_id=saved["id"], payload=monte_carlo.to_dict())
        self.risk_repository.create_result(asset_id=asset["id"], analysis_id=saved["id"], payload=risk.to_dict())
        self.decision_repository.create_result(asset_id=asset["id"], analysis_id=saved["id"], payload=consensus.to_dict())

        return {
            "symbol": asset["symbol"],
            "timeframe": timeframe,
            "horizon_days": horizon_days,
            "analysis_type": "full",
            "technical": technical.to_dict(),
            "monte_carlo": monte_carlo.to_dict(),
            "risk": risk.to_dict(),
            "consensus": consensus.to_dict(),
            "saved_analysis_id": saved["id"],
        }
