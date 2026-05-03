from app.repositories.asset_repository import AssetRepository
from app.repositories.risk_repository import RiskRepository


def test_risk_repository_create_and_latest(app):
    with app.app_context():
        asset = AssetRepository().create_asset(symbol="RSK", name="Risk Test", asset_type="crypto")
        repo = RiskRepository()
        created = repo.create_result(asset_id=asset["id"], payload={"b": 2})
        latest = repo.get_latest_for_asset(asset["id"])
        assert created["id"] == latest["id"]
