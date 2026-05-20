from collections.abc import Iterator
from threading import Lock

from flask import Response, current_app, jsonify


class RealtimeService:
    _stream_state_lock = Lock()
    _active_stream_connections = 0

    @staticmethod
    def get_status_payload() -> dict:
        enabled = bool(current_app.config.get("ENABLE_REALTIME", False))
        status = "enabled" if enabled else "disabled"
        return {"module": "realtime", "enabled": enabled, "status": status}

    @classmethod
    def _sse_event(cls, event: str, data: dict) -> str:
        import json

        return f"event: {event}\ndata: {json.dumps(data)}\n\n"

    @classmethod
    def _stream_generator(cls, symbol: str) -> Iterator[str]:
        try:
            yield cls._sse_event("connected", {"symbol": symbol.upper(), "transport": "sse"})
            yield cls._sse_event("heartbeat", {"ok": True})
        except GeneratorExit:
            current_app.logger.info("Realtime stream disconnected by client")
            raise
        finally:
            with cls._stream_state_lock:
                cls._active_stream_connections = max(0, cls._active_stream_connections - 1)

    @classmethod
    def stream_response_or_error(cls, symbol: str):
        if not bool(current_app.config.get("ENABLE_REALTIME", False)):
            return jsonify({"error": {"code": "realtime_disabled", "message": "Realtime streaming is disabled"}}), 503

        max_connections = int(current_app.config.get("REALTIME_MAX_CONNECTIONS", 5))
        with cls._stream_state_lock:
            if cls._active_stream_connections >= max_connections:
                return jsonify({"error": {"code": "realtime_connection_limit", "message": "Too many realtime connections"}}), 429
            cls._active_stream_connections += 1

        response = Response(cls._stream_generator(symbol), mimetype="text/event-stream")
        response.headers["Cache-Control"] = "no-cache"
        response.headers["Connection"] = "keep-alive"
        response.headers["X-Realtime-Transport"] = "sse"
        return response
