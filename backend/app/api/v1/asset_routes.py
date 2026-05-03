from flask import Blueprint, jsonify

from app.services.assets.asset_service import AssetService
from app.services.market_data.sample_provider import SampleMarketDataProvider


asset_bp = Blueprint("assets", __name__)


@asset_bp.get("")
def list_assets():
    service = AssetService()
    return jsonify({"items": service.list_assets()}), 200


@asset_bp.get("/<string:symbol>")
def get_asset(symbol: str):
    service = AssetService()
    return jsonify(service.get_asset(symbol)), 200


@asset_bp.post("/sync-sample")
def sync_sample_assets():
    service = AssetService()
    assets = service.sync_assets_from_provider(SampleMarketDataProvider())
    return jsonify({"synced": len(assets), "items": assets}), 200
