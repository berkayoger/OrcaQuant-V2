from __future__ import annotations

from app.core.errors import error_codes
from app.core.errors.exceptions import ValidationError
from app.extensions import db
from app.models.asset import Asset


class AssetRepository:
    def create_asset(
        self,
        symbol: str,
        name: str,
        asset_type: str = "crypto",
        provider: str = "manual",
        provider_id: str | None = None,
        metadata_json: dict | None = None,
    ) -> dict:
        normalized_symbol = symbol.upper().strip()
        if self.get_by_symbol(normalized_symbol):
            raise ValidationError("Asset symbol already exists", error_code=error_codes.DUPLICATE_RESOURCE_ERROR)

        asset = Asset(
            symbol=normalized_symbol,
            name=name,
            asset_type=asset_type,
            provider=provider,
            provider_id=provider_id,
            metadata_json=metadata_json,
            is_active=True,
        )
        db.session.add(asset)
        db.session.commit()
        return self._to_dict(asset)

    def upsert_asset(self, symbol: str, name: str, asset_type: str = "crypto", provider: str = "manual", provider_id: str | None = None, metadata_json: dict | None = None) -> dict:
        normalized_symbol = symbol.upper().strip()
        asset = Asset.query.filter_by(symbol=normalized_symbol).one_or_none()
        if not asset:
            return self.create_asset(normalized_symbol, name, asset_type, provider, provider_id, metadata_json)

        asset.name = name
        asset.asset_type = asset_type
        asset.provider = provider
        asset.provider_id = provider_id
        asset.metadata_json = metadata_json
        asset.is_active = True
        db.session.commit()
        return self._to_dict(asset)

    def get_by_symbol(self, symbol: str) -> dict | None:
        asset = Asset.query.filter_by(symbol=symbol.upper().strip()).one_or_none()
        return self._to_dict(asset) if asset else None

    def get_by_id(self, asset_id: str) -> dict | None:
        asset = Asset.query.filter_by(id=asset_id).one_or_none()
        return self._to_dict(asset) if asset else None

    def list_active_assets(self, limit: int = 100, offset: int = 0) -> list[dict]:
        rows = Asset.query.filter_by(is_active=True).order_by(Asset.symbol.asc()).offset(offset).limit(limit).all()
        return [self._to_dict(row) for row in rows]

    def _to_dict(self, asset: Asset) -> dict:
        return {
            "id": asset.id,
            "symbol": asset.symbol,
            "name": asset.name,
            "asset_type": asset.asset_type,
            "provider": asset.provider,
            "provider_id": asset.provider_id,
            "is_active": asset.is_active,
            "metadata_json": asset.metadata_json,
        }
