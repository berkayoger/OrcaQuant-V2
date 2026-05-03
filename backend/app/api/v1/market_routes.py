from flask import Blueprint, jsonify


market_bp = Blueprint("market", __name__)


@market_bp.get("/")
def get_market_status():
    return jsonify({"module": "market", "status": "not_implemented"}), 200
