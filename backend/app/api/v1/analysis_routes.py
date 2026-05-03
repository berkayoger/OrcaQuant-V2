from flask import Blueprint, jsonify, request

from app.services.analysis.asset_analysis_service import AssetAnalysisService


analysis_bp = Blueprint("analysis", __name__)


@analysis_bp.get("/")
def get_analysis_status():
    return jsonify({"module": "analysis", "status": "ready"}), 200


@analysis_bp.get("/<symbol>/technical")
def get_technical_analysis(symbol: str):
    timeframe = request.args.get("timeframe", "1d")
    limit = int(request.args.get("limit", 200))
    payload = AssetAnalysisService().run_technical_analysis(symbol=symbol, timeframe=timeframe, limit=limit)
    return jsonify(payload), 200


@analysis_bp.get("/<symbol>/latest")
def get_latest_analysis(symbol: str):
    analysis_type = request.args.get("analysis_type", "technical")
    payload = AssetAnalysisService().get_latest_analysis(symbol=symbol, analysis_type=analysis_type)
    if payload is None:
        return jsonify({"error": "analysis_not_found", "symbol": symbol.upper(), "analysis_type": analysis_type}), 404
    return jsonify(payload), 200


@analysis_bp.post("/<symbol>/scenario-risk")
def post_scenario_risk_analysis(symbol: str):
    body = request.get_json(silent=True) or {}
    timeframe = body.get("timeframe", "1d")
    limit = int(body.get("limit", 200))
    horizon_days = int(body.get("horizon_days", 14))
    targets = body.get("targets", [])
    if horizon_days < 1 or horizon_days > 365:
        return jsonify({"error": "invalid_horizon_days"}), 400
    for target in targets:
        if target.get("direction") not in {"above", "below"}:
            return jsonify({"error": "invalid_target_direction"}), 400
    payload = AssetAnalysisService().run_scenario_risk_analysis(
        symbol=symbol,
        timeframe=timeframe,
        limit=limit,
        horizon_days=horizon_days,
        targets=targets,
    )
    return jsonify(payload), 200
