from app.repositories.asset_repository import AssetRepository
from app.repositories.monte_carlo_repository import MonteCarloRepository


def test_monte_carlo_repository_create_and_latest(app):
    with app.app_context():
        asset = AssetRepository().create_asset(symbol="MCT", name="MC Test", asset_type="crypto")
        repo = MonteCarloRepository()
        created = repo.create_result(asset_id=asset["id"], payload={"a": 1})
        latest = repo.get_latest_for_asset(asset["id"])
        assert created["id"] == latest["id"]
