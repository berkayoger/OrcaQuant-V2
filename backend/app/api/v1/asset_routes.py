from flask import Blueprint, jsonify


asset_bp = Blueprint("assets", __name__)


@asset_bp.get("/")
def get_assets_status():
    return jsonify({"module": "assets", "status": "not_implemented"}), 200
