from app.repositories.analysis_repository import AnalysisRepository
from app.services.assets.asset_service import AssetService
from app.services.market_data.sample_provider import SampleMarketDataProvider


def test_analysis_repository_create_and_get_latest(app):
    with app.app_context():
        AssetService().sync_assets_from_provider(SampleMarketDataProvider())
        from app.repositories.asset_repository import AssetRepository

        asset = AssetRepository().get_by_symbol("BTC")
        repo = AnalysisRepository()
        created = repo.create_analysis_result(asset["id"], "technical", {"signal_score": 64.2})
        latest = repo.get_latest_for_asset(asset["id"], "technical")
        assert created["id"] == latest["id"]
        assert latest["payload_json"]["signal_score"] == 64.2
