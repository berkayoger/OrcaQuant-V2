from app.repositories.analysis_repository import AnalysisRepository
from app.repositories.asset_repository import AssetRepository
from app.repositories.decision_repository import DecisionRepository
from app.repositories.monte_carlo_repository import MonteCarloRepository
from app.repositories.risk_repository import RiskRepository
from app.services.analysis.asset_analysis_service import AssetAnalysisService
from app.services.market_data.ohlcv_service import OhlcvService


def test_full_analysis_service_persists_all_payloads(app):
    with app.app_context():
        AssetRepository().create_asset("BTC", "Bitcoin")
        OhlcvService().sync_ohlcv("BTC", limit=120)

        result = AssetAnalysisService().run_full_analysis(
            "BTC",
            limit=120,
            horizon_days=14,
            targets=[{"name": "target_up", "direction": "above", "price": 30000}],
        )
        asset = AssetRepository().get_by_symbol("BTC")
        latest_analysis = AnalysisRepository().get_latest_for_asset(asset["id"], analysis_type="full")
        latest_monte_carlo = MonteCarloRepository().get_latest_for_asset(asset["id"])
        latest_risk = RiskRepository().get_latest_for_asset(asset["id"])
        latest_decision = DecisionRepository().get_latest_for_asset(asset["id"])

        assert result["analysis_type"] == "full"
        assert "technical" in result
        assert "monte_carlo" in result
        assert "risk" in result
        assert "consensus" in result
        assert latest_analysis["id"] == result["saved_analysis_id"]
        assert latest_monte_carlo["analysis_id"] == result["saved_analysis_id"]
        assert latest_risk["analysis_id"] == result["saved_analysis_id"]
        assert latest_decision["analysis_id"] == result["saved_analysis_id"]
        assert latest_decision["payload"]["decision"] == result["consensus"]["decision"]
