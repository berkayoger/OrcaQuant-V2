from app.repositories.asset_repository import AssetRepository
from app.repositories.decision_repository import DecisionRepository


def test_decision_repository_create_and_get_latest(app):
    with app.app_context():
        asset = AssetRepository().create_asset("BTC", "Bitcoin")
        repo = DecisionRepository()

        saved = repo.create_result(asset_id=asset["id"], payload={"decision": "WATCH"})
        latest = repo.get_latest_for_asset(asset["id"])

        assert saved["asset_id"] == asset["id"]
        assert saved["payload"] == {"decision": "WATCH"}
        assert latest is not None
        assert latest["id"] == saved["id"]
        assert latest["created_at"] is not None
