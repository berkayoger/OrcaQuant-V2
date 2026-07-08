from flask import Blueprint, jsonify, request

from app.services.dashboard.market_cockpit_service import MarketCockpitService
from app.services.product.orca_product_suite import OrcaProductSuite


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


@dashboard_bp.get("/radar/variants")
def get_radar_variants():
    return jsonify(OrcaProductSuite().build_radar_variants(symbols=_symbols_from_query("symbols"))), 200


@dashboard_bp.get("/daily-brief")
def get_daily_brief():
    return jsonify(OrcaProductSuite().build_daily_brief(symbols=_symbols_from_query("symbols"))), 200


@dashboard_bp.get("/assets/<symbol>")
def get_asset_detail(symbol: str):
    return jsonify(OrcaProductSuite().build_asset_detail(symbol)), 200


@dashboard_bp.post("/portfolio/assistant")
def build_portfolio_assistant():
    payload = request.get_json(silent=True) or {}
    holdings = payload.get("holdings") if isinstance(payload.get("holdings"), list) else []
    return jsonify(OrcaProductSuite().build_portfolio_assistant(holdings)), 200


@dashboard_bp.get("/plans")
def get_plan_entitlements():
    return jsonify(OrcaProductSuite().build_plan_entitlements()), 200


@dashboard_bp.get("/admin/analytics")
def get_admin_product_analytics():
    return jsonify(OrcaProductSuite().build_admin_analytics()), 200


@dashboard_bp.get("/features/suite")
def get_product_feature_suite():
    return jsonify(OrcaProductSuite().build_feature_suite(symbols=_symbols_from_query("symbols"))), 200
