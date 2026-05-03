import pytest

from app.core.errors.exceptions import ValidationError
from app.repositories.asset_repository import AssetRepository


def test_asset_create_and_get(app):
    with app.app_context():
        repo = AssetRepository()
        created = repo.create_asset(symbol="btc", name="Bitcoin")
        fetched = repo.get_by_symbol("BTC")
        assert created["symbol"] == "BTC"
        assert fetched["id"] == created["id"]


def test_asset_duplicate_prevented(app):
    with app.app_context():
        repo = AssetRepository()
        repo.create_asset(symbol="ETH", name="Ethereum")
        with pytest.raises(ValidationError):
            repo.create_asset(symbol="eth", name="Ethereum")
