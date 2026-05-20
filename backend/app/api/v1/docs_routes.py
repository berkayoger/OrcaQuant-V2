from flask import Blueprint, jsonify


docs_bp = Blueprint("docs", __name__)


def _build_minimal_openapi() -> dict:
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "OrcaQuant V2 API",
            "version": "1.1.0",
            "description": "Migration-phase OpenAPI foundation for V2 auth, analysis, docs, and placeholder modules.",
        },
        "paths": {
            "/api/v1/auth/register": {"post": {"summary": "Register", "responses": {"201": {"description": "Authenticated"}}}},
            "/api/v1/auth/login": {"post": {"summary": "Login", "responses": {"200": {"description": "Authenticated"}}}},
            "/api/v1/auth/refresh": {"post": {"summary": "Rotate refresh token", "responses": {"200": {"description": "Token pair returned"}}}},
            "/api/v1/auth/logout": {"post": {"summary": "Logout", "responses": {"200": {"description": "Session revoked"}}}},
            "/api/v1/user/me": {"get": {"summary": "Current user", "responses": {"200": {"description": "User details"}}}},
            "/api/v1/analysis/technical/latest": {"get": {"summary": "Latest technical analysis", "responses": {"200": {"description": "Analysis result"}}}},
            "/api/v1/analysis/scenario-risk": {"post": {"summary": "Scenario risk", "responses": {"200": {"description": "Analysis result"}}}},
            "/api/v1/analysis/full": {"post": {"summary": "Run full analysis", "responses": {"200": {"description": "Analysis result"}}}},
            "/api/v1/billing/status": {"get": {"summary": "Billing module status", "responses": {"200": {"description": "Billing status"}}}},
            "/api/v1/billing/initiate": {"post": {"summary": "Billing initiate placeholder", "responses": {"501": {"description": "Disabled or not implemented"}}}},
            "/api/v1/market/realtime/status": {"get": {"summary": "Realtime module status", "responses": {"200": {"description": "Realtime status"}}}},
            "/api/v1/docs/": {"get": {"summary": "Docs status", "responses": {"200": {"description": "Docs endpoint status"}}}},
            "/api/v1/docs/openapi.json": {"get": {"summary": "OpenAPI document", "responses": {"200": {"description": "OpenAPI JSON"}}}},
        },
        "components": {
            "schemas": {
                "AuthResponse": {"type": "object", "required": ["access_token", "refresh_token", "token_type", "user"], "properties": {"access_token": {"type": "string"}, "refresh_token": {"type": "string"}, "token_type": {"type": "string", "example": "bearer"}, "user": {"$ref": "#/components/schemas/User"}}},
                "User": {"type": "object", "required": ["id", "email", "role"], "properties": {"id": {"type": "string"}, "email": {"type": "string", "format": "email"}, "role": {"type": "string"}, "plan_code": {"type": ["string", "null"]}}},
                "BillingStatus": {"type": "object", "properties": {"module": {"type": "string"}, "enabled": {"type": "boolean"}, "status": {"type": "string"}}},
                "RealtimeStatus": {"type": "object", "properties": {"module": {"type": "string"}, "enabled": {"type": "boolean"}, "status": {"type": "string"}}},
                "ErrorResponse": {"type": "object", "properties": {"error": {"type": "object", "properties": {"code": {"type": "string"}, "message": {"type": "string"}}}}},
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
