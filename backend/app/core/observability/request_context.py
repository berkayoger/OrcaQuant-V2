"""Request context helpers."""

from __future__ import annotations

from uuid import uuid4

from flask import Flask, g, request


REQUEST_ID_HEADER = "X-Request-ID"


def register_request_id_middleware(app: Flask) -> None:
    @app.before_request
    def _set_request_id() -> None:
        request_id = request.headers.get(REQUEST_ID_HEADER) or str(uuid4())
        g.request_id = request_id

    @app.after_request
    def _add_request_id_header(response):
        response.headers.setdefault(REQUEST_ID_HEADER, getattr(g, "request_id", str(uuid4())))
        return response
