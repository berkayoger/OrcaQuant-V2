from flask import Blueprint, jsonify


docs_bp = Blueprint("docs", __name__)


def _build_minimal_openapi() -> dict:
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "OrcaQuant V2 API",
            "version": "1.0.0",
            "description": "Minimal migration-phase OpenAPI document for core V2 status and auth flows.",
        },
        "paths": {
            "/api/v1/auth/login": {"post": {"summary": "Login", "responses": {"200": {"description": "Authenticated"}}}},
            "/api/v1/auth/refresh": {"post": {"summary": "Rotate refresh token", "responses": {"200": {"description": "Token pair returned"}}}},
            "/api/v1/analysis/full": {"post": {"summary": "Run full analysis", "responses": {"200": {"description": "Analysis result"}}}},
            "/api/v1/billing/status": {"get": {"summary": "Billing module status", "responses": {"200": {"description": "Billing status"}}}},
            "/api/v1/realtime/status": {"get": {"summary": "Realtime module status", "responses": {"200": {"description": "Realtime status"}}}},
        },
        "components": {
            "schemas": {
                "AuthResponse": {
                    "type": "object",
                    "required": ["access_token", "refresh_token", "token_type", "user"],
                    "properties": {
                        "access_token": {"type": "string"},
                        "refresh_token": {"type": "string"},
                        "token_type": {"type": "string", "example": "bearer"},
                        "user": {
                            "type": "object",
                            "required": ["id", "email", "role"],
                            "properties": {
                                "id": {"type": "string"},
                                "email": {"type": "string", "format": "email"},
                                "role": {"type": "string"},
                                "plan_code": {"type": ["string", "null"]},
                            },
                        },
                    },
                },
                "AnalysisResponse": {"type": "object", "properties": {"status": {"type": "string"}, "data": {"type": "object"}}},
                "BillingStatus": {"type": "object", "properties": {"module": {"type": "string"}, "status": {"type": "string"}}},
                "RealtimeStatus": {"type": "object", "properties": {"module": {"type": "string"}, "status": {"type": "string"}}},
                "ErrorResponse": {
                    "type": "object",
                    "properties": {
                        "error": {
                            "type": "object",
                            "properties": {"code": {"type": "string"}, "message": {"type": "string"}},
                        }
                    },
                },
            }
        },
    }


@docs_bp.get("/")
def get_docs_status():
    return jsonify(
        {
            "module": "docs",
            "status": "ok",
            "message": "OpenAPI document available at /api/v1/docs/openapi.json",
            "openapi_url": "/api/v1/docs/openapi.json",
        }
    ), 200


@docs_bp.get("/openapi.json")
def get_openapi_json():
    return jsonify(_build_minimal_openapi()), 200
