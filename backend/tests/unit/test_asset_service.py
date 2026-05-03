from app.services.assets.asset_service import AssetService
from app.services.market_data.sample_provider import SampleMarketDataProvider


def test_asset_service_sync_and_list(app):
    with app.app_context():
        service = AssetService()
        synced = service.sync_assets_from_provider(SampleMarketDataProvider())
        listed = service.list_assets()
        assert len(synced) == 5
        assert len(listed) == 5
