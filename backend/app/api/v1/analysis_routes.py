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
