from app.services.assets.asset_service import AssetService
from app.services.market_data.sample_provider import SampleMarketDataProvider


def seed_assets() -> list[dict]:
    service = AssetService()
    return service.sync_assets_from_provider(SampleMarketDataProvider())
