from flask import Blueprint, jsonify


portfolio_bp = Blueprint("portfolio", __name__)


@portfolio_bp.get("/")
def get_portfolio_status():
    return jsonify({"module": "portfolio", "status": "not_implemented"}), 200
