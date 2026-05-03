from __future__ import annotations

from app.core.errors.exceptions import NotFoundError
from app.repositories.asset_repository import AssetRepository


class AssetService:
    def __init__(self, asset_repository: AssetRepository | None = None) -> None:
        self.asset_repository = asset_repository or AssetRepository()

    def sync_assets_from_provider(self, provider) -> list[dict]:
        synced = []
        for row in provider.list_assets():
            synced.append(
                self.asset_repository.upsert_asset(
                    symbol=row["symbol"],
                    name=row["name"],
                    asset_type=row.get("asset_type", "crypto"),
                    provider=row.get("provider", "sample"),
                    provider_id=row.get("provider_id"),
                    metadata_json=row.get("metadata_json"),
                )
            )
        return synced

    def list_assets(self, limit: int = 100, offset: int = 0) -> list[dict]:
        return self.asset_repository.list_active_assets(limit=limit, offset=offset)

    def get_asset(self, symbol: str) -> dict:
        asset = self.asset_repository.get_by_symbol(symbol)
        if not asset:
            raise NotFoundError(f"Asset not found: {symbol}")
        return asset
