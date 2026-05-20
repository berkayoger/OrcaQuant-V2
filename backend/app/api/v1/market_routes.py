from flask import Blueprint, jsonify, request

from app.core.security.auth_guard import require_auth
from app.services.market_data.ohlcv_service import OhlcvService
from app.services.realtime.realtime_service import RealtimeService


market_bp = Blueprint("market", __name__)


@market_bp.get("/<string:symbol>/ohlcv")
def get_ohlcv(symbol: str):
    timeframe = request.args.get("timeframe", "1d")
    limit = int(request.args.get("limit", 200))
    service = OhlcvService()
    return jsonify({"symbol": symbol.upper(), "timeframe": timeframe, "rows": service.get_ohlcv(symbol, timeframe, limit)}), 200


@market_bp.post("/<string:symbol>/sync")
def sync_ohlcv(symbol: str):
    timeframe = request.args.get("timeframe", "1d")
    limit = int(request.args.get("limit", 200))
    service = OhlcvService()
    return jsonify(service.sync_ohlcv(symbol, timeframe, limit)), 200


@market_bp.get("/realtime/status")
def realtime_status():
    return jsonify(RealtimeService.get_status_payload()), 200


@market_bp.get("/realtime/stream/<string:symbol>")
@require_auth
def realtime_stream(symbol: str):
    return RealtimeService.stream_response_or_error(symbol)
