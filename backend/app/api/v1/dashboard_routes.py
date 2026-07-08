from flask import Blueprint, jsonify

from app.services.dashboard.market_cockpit_service import MarketCockpitService


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/")
def get_market_cockpit():
    return jsonify(MarketCockpitService().build_cockpit()), 200


@dashboard_bp.get("/radar")
def get_orca_radar():
    return jsonify(MarketCockpitService().build_radar()), 200
