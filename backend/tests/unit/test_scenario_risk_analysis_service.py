from app.services.analysis.asset_analysis_service import AssetAnalysisService
from app.services.assets.asset_service import AssetService
from app.services.market_data.sample_provider import SampleMarketDataProvider


def test_scenario_risk_service_persists(app):
    with app.app_context():
        AssetService().sync_assets_from_provider(SampleMarketDataProvider())
        payload = AssetAnalysisService().run_scenario_risk_analysis("BTC", limit=120, horizon_days=14)
        assert payload["analysis_type"] == "scenario_risk"
        assert payload["saved_analysis_id"]
