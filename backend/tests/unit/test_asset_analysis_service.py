from app.services.analysis.asset_analysis_service import AssetAnalysisService
from app.services.assets.asset_service import AssetService
from app.services.market_data.sample_provider import SampleMarketDataProvider


def test_asset_analysis_service_runs_technical_analysis(app):
    with app.app_context():
        AssetService().sync_assets_from_provider(SampleMarketDataProvider())
        payload = AssetAnalysisService().run_technical_analysis("BTC", timeframe="1d", limit=120)
        assert payload["symbol"] == "BTC"
        assert payload["analysis_type"] == "technical"
        assert 0 <= payload["result"]["signal_score"] <= 100
        assert payload["saved_analysis_id"]
