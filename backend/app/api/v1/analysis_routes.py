from flask import Blueprint, jsonify, request

from app.core.security.auth_guard import require_auth
from app.core.security.usage_guard import enforce_usage_limit
from app.services.analysis.asset_analysis_service import AssetAnalysisService


analysis_bp = Blueprint("analysis", __name__)


def _parse_int(name: str, value: object, min_value: int, max_value: int) -> tuple[int | None, dict | None]:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None, {"error": f"invalid_{name}", "message": f"{name} must be an integer"}
    if parsed < min_value or parsed > max_value:
        return None, {"error": f"invalid_{name}", "message": f"{name} must be between {min_value} and {max_value}"}
    return parsed, None


def _normalize_symbol(symbol: str) -> str:
    return symbol.strip().upper()


def _response_from_service_payload(payload: object):
    if isinstance(payload, tuple) and len(payload) == 2:
        body, status = payload
        return jsonify(body), int(status)
    return jsonify(payload), 200


@analysis_bp.get("/")
def get_analysis_status():
    return jsonify({"module": "analysis", "status": "ready"}), 200


@analysis_bp.get("/<symbol>/technical")
@require_auth
@enforce_usage_limit("technical_analysis")
def get_technical_analysis(symbol: str):
    timeframe = request.args.get("timeframe", "1d")
    limit, err = _parse_int("limit", request.args.get("limit", 200), 50, 1000)
    if err:
        return jsonify(err), 400
    payload = AssetAnalysisService().run_technical_analysis(symbol=_normalize_symbol(symbol), timeframe=timeframe, limit=limit)
    return _response_from_service_payload(payload)


@analysis_bp.get("/<symbol>/latest")
@require_auth
def get_latest_analysis(symbol: str):
    analysis_type = request.args.get("analysis_type", "technical")
    payload = AssetAnalysisService().get_latest_analysis(symbol=_normalize_symbol(symbol), analysis_type=analysis_type)
    if payload is None:
        return jsonify({"error": "analysis_not_found", "symbol": symbol.upper(), "analysis_type": analysis_type}), 404
    return _response_from_service_payload(payload)


@analysis_bp.post("/<symbol>/scenario-risk")
@require_auth
@enforce_usage_limit("scenario_risk")
def post_scenario_risk_analysis(symbol: str):
    body = request.get_json(silent=True) or {}
    timeframe = body.get("timeframe", "1d")
    limit, err = _parse_int("limit", body.get("limit", 200), 50, 1000)
    if err:
        return jsonify(err), 400
    horizon_days, err = _parse_int("horizon_days", body.get("horizon_days", 14), 1, 365)
    if err:
        return jsonify(err), 400
    targets = body.get("targets", [])
    for target in targets:
        if target.get("direction") not in {"above", "below"}:
            return jsonify({"error": "invalid_target_direction"}), 400
    payload = AssetAnalysisService().run_scenario_risk_analysis(symbol=_normalize_symbol(symbol), timeframe=timeframe, limit=limit, horizon_days=horizon_days, targets=targets)
    return _response_from_service_payload(payload)


@analysis_bp.post("/<symbol>/full")
@require_auth
@enforce_usage_limit("full_analysis")
def post_full_analysis(symbol: str):
    body = request.get_json(silent=True) or {}
    timeframe = body.get("timeframe", "1d")
    limit, err = _parse_int("limit", body.get("limit", 200), 50, 1000)
    if err:
        return jsonify(err), 400
    horizon_days, err = _parse_int("horizon_days", body.get("horizon_days", 14), 1, 365)
    if err:
        return jsonify(err), 400
    targets = body.get("targets", [])
    for target in targets:
        if target.get("direction") not in {"above", "below"}:
            return jsonify({"error": "invalid_target_direction"}), 400

    payload = AssetAnalysisService().run_full_analysis(symbol=_normalize_symbol(symbol), timeframe=timeframe, limit=limit, horizon_days=horizon_days, targets=targets)
    return _response_from_service_payload(payload)
