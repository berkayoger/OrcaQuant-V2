from flask import Blueprint, jsonify


watchlist_bp = Blueprint("watchlist", __name__)


@watchlist_bp.get("/")
def get_watchlist_status():
    return jsonify({"module": "watchlist", "status": "not_implemented"}), 200
