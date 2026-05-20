from collections.abc import Iterator
from threading import Lock

from flask import Blueprint, Response, current_app, jsonify, request

from app.core.security.auth_guard import require_auth
from app.services.market_data.ohlcv_service import OhlcvService


market_bp = Blueprint("market", __name__)
_stream_state_lock = Lock()
_active_stream_connections = 0


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
    enabled = bool(current_app.config.get("ENABLE_REALTIME", False))
    status = "enabled" if enabled else "disabled"
    return jsonify({"module": "realtime", "enabled": enabled, "status": status}), 200


def _sse_event(event: str, data: dict) -> str:
    import json

    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _realtime_stream_generator(symbol: str) -> Iterator[str]:
    try:
        yield _sse_event("connected", {"symbol": symbol.upper(), "transport": "sse"})
        yield _sse_event("heartbeat", {"ok": True})
    except GeneratorExit:
        current_app.logger.info("Realtime stream disconnected by client")
        raise
    finally:
        global _active_stream_connections
        with _stream_state_lock:
            _active_stream_connections = max(0, _active_stream_connections - 1)


@market_bp.get("/realtime/stream/<string:symbol>")
@require_auth
def realtime_stream(symbol: str):
    if not bool(current_app.config.get("ENABLE_REALTIME", False)):
        return jsonify({"error": {"code": "realtime_disabled", "message": "Realtime streaming is disabled"}}), 503

    max_connections = int(current_app.config.get("REALTIME_MAX_CONNECTIONS", 5))
    global _active_stream_connections
    with _stream_state_lock:
        if _active_stream_connections >= max_connections:
            return jsonify({"error": {"code": "realtime_connection_limit", "message": "Too many realtime connections"}}), 429
        _active_stream_connections += 1

    response = Response(_realtime_stream_generator(symbol), mimetype="text/event-stream")
    response.headers["Cache-Control"] = "no-cache"
    response.headers["Connection"] = "keep-alive"
    response.headers["X-Realtime-Transport"] = "sse"
    return response
