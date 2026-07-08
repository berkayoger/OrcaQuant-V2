from flask import Blueprint, jsonify, request

from app.services.dashboard.market_cockpit_service import MarketCockpitService


dashboard_bp = Blueprint("dashboard", __name__)


def _symbols_from_query(param: str) -> list[str]:
    raw = request.args.get(param, "")
    return [part.strip() for part in raw.split(",") if part.strip()]


@dashboard_bp.get("/")
def get_market_cockpit():
    return jsonify(
        MarketCockpitService().build_cockpit(
            symbols=_symbols_from_query("symbols"),
            watchlist_symbols=_symbols_from_query("watchlist"),
        )
    ), 200


@dashboard_bp.get("/radar")
def get_orca_radar():
    return jsonify(MarketCockpitService().build_radar(symbols=_symbols_from_query("symbols"))), 200
