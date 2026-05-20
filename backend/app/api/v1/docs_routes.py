from flask import Blueprint, jsonify


docs_bp = Blueprint("docs", __name__)


USAGE_HEADERS = {
    "X-Usage-Used": {"description": "Updated usage count after this request", "schema": {"type": "integer"}},
    "X-Usage-Quota": {"description": "Total quota for the feature", "schema": {"type": "integer"}},
    "X-Usage-Remaining": {"description": "Remaining requests in the current quota window", "schema": {"type": "integer"}},
}


def _build_minimal_openapi() -> dict:
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "OrcaQuant V2 API",
            "version": "1.1.0",
            "description": "V2 OpenAPI for implemented auth, user, analysis, billing, market, and docs routes.",
        },
        "paths": {
            "/api/v1/auth/register": {"post": {"summary": "Register", "responses": {"201": {"description": "Authenticated", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AuthResponse"}}}}, "400": {"description": "Validation error", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}}}}},
            "/api/v1/auth/login": {"post": {"summary": "Login", "responses": {"200": {"description": "Authenticated", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AuthResponse"}}}}, "401": {"description": "Unauthorized", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}}}}},
            "/api/v1/auth/refresh": {"post": {"summary": "Rotate refresh token", "responses": {"200": {"description": "Token pair returned", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/AuthResponse"}}}}}}},
            "/api/v1/auth/logout": {"post": {"summary": "Logout", "security": [{"BearerAuth": []}], "responses": {"200": {"description": "Session revoked"}}}},
            "/api/v1/me/": {"get": {"summary": "Current user", "security": [{"BearerAuth": []}], "responses": {"200": {"description": "User details", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/User"}}}}, "401": {"description": "Unauthorized", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}}}}},
            "/api/v1/me/usage": {"get": {"summary": "Usage status", "security": [{"BearerAuth": []}], "responses": {"200": {"description": "Usage details", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/UsageStatus"}}}}}}},
            "/api/v1/limits/status": {"get": {"summary": "Plan limits status", "security": [{"BearerAuth": []}], "responses": {"200": {"description": "Limits and usage status", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/LimitsStatus"}}}}, "401": {"description": "Unauthorized", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}}}}},
            "/api/v1/analysis/{symbol}/technical": {"get": {"summary": "Technical analysis", "security": [{"BearerAuth": []}], "parameters": [{"$ref": "#/components/parameters/SymbolParam"}], "responses": {"200": {"description": "Analysis result", "headers": USAGE_HEADERS, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/TechnicalAnalysisResponse"}}}}, "400": {"description": "Invalid input", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}}}}},
            "/api/v1/analysis/{symbol}/latest": {"get": {"summary": "Latest analysis", "security": [{"BearerAuth": []}], "parameters": [{"$ref": "#/components/parameters/SymbolParam"}], "responses": {"200": {"description": "Latest analysis", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/LatestAnalysisResponse"}}}}, "404": {"description": "Not found", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}}}}},
            "/api/v1/analysis/{symbol}/scenario-risk": {"post": {"summary": "Scenario risk", "security": [{"BearerAuth": []}], "parameters": [{"$ref": "#/components/parameters/SymbolParam"}], "responses": {"200": {"description": "Analysis result", "headers": USAGE_HEADERS, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ScenarioRiskResponse"}}}}, "400": {"description": "Invalid input", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}}}}},
            "/api/v1/analysis/{symbol}/full": {"post": {"summary": "Run full analysis", "security": [{"BearerAuth": []}], "parameters": [{"$ref": "#/components/parameters/SymbolParam"}], "responses": {"200": {"description": "Analysis result", "headers": USAGE_HEADERS, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/FullAnalysisResponse"}}}}, "400": {"description": "Invalid input", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/ErrorResponse"}}}}}}},
            "/api/v1/billing/status": {"get": {"summary": "Billing module status", "responses": {"200": {"description": "Billing status", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BillingStatus"}}}}}}},
            "/api/v1/market/realtime/status": {"get": {"summary": "Realtime module status", "responses": {"200": {"description": "Realtime status", "content": {"application/json": {"schema": {"$ref": "#/components/schemas/RealtimeStatus"}}}}}}},
            "/api/v1/docs/": {"get": {"summary": "Docs status", "responses": {"200": {"description": "Docs endpoint status"}}}},
            "/api/v1/docs/openapi.json": {"get": {"summary": "OpenAPI document", "responses": {"200": {"description": "OpenAPI JSON"}}}},
        },
        "components": {
            "securitySchemes": {"BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}},
            "parameters": {"SymbolParam": {"name": "symbol", "in": "path", "required": True, "schema": {"type": "string"}, "description": "Asset symbol, e.g. BTCUSDT"}},
            "schemas": {
                "AuthResponse": {"type": "object", "required": ["access_token", "refresh_token", "token_type", "user"], "properties": {"access_token": {"type": "string"}, "refresh_token": {"type": "string"}, "token_type": {"type": "string", "example": "bearer"}, "user": {"$ref": "#/components/schemas/User"}}},
                "User": {"type": "object", "required": ["id", "email", "role"], "properties": {"id": {"type": "string"}, "email": {"type": "string", "format": "email"}, "role": {"type": "string"}, "plan_code": {"type": "string", "nullable": True}, "subscription_status": {"type": "string", "nullable": True}}},
                "UsageStatus": {"type": "object", "properties": {"feature": {"type": "string"}, "used": {"type": "integer"}, "quota": {"type": "integer"}, "remaining": {"type": "integer"}, "exhausted": {"type": "boolean"}}},
                "LimitsPlan": {
                    "type": "object",
                    "required": ["id", "code", "name"],
                    "properties": {
                        "id": {"type": "string"},
                        "code": {"type": "string"},
                        "name": {"type": "string"},
                    },
                },
                "LimitsFeatureStatus": {
                    "type": "object",
                    "required": ["feature_key", "used", "quota", "remaining", "percent", "warning_level", "exhausted"],
                    "properties": {
                        "feature_key": {"type": "string"},
                        "used": {"type": "integer"},
                        "quota": {"type": "integer"},
                        "remaining": {"type": "integer"},
                        "percent": {"type": "integer"},
                        "warning_level": {"type": "string", "nullable": True},
                        "exhausted": {"type": "boolean"},
                    },
                },
                "LimitsStatus": {
                    "type": "object",
                    "required": ["plan_id", "plan", "features"],
                    "properties": {
                        "plan_id": {"type": "string", "nullable": True},
                        "plan": {"nullable": True, "allOf": [{"$ref": "#/components/schemas/LimitsPlan"}]},
                        "features": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/LimitsFeatureStatus"},
                        },
                    },
                },
                "TechnicalAnalysisResponse": {"type": "object", "additionalProperties": True},
                "LatestAnalysisResponse": {"type": "object", "additionalProperties": True},
                "ScenarioRiskResponse": {"type": "object", "additionalProperties": True},
                "FullAnalysisResponse": {"type": "object", "additionalProperties": True},
                "BillingStatus": {"type": "object", "properties": {"module": {"type": "string"}, "enabled": {"type": "boolean"}, "status": {"type": "string"}}},
                "RealtimeStatus": {"type": "object", "properties": {"module": {"type": "string"}, "enabled": {"type": "boolean"}, "status": {"type": "string"}}},
                "ErrorResponse": {"type": "object", "properties": {"error": {"oneOf": [{"type": "string"}, {"type": "object", "properties": {"code": {"type": "string"}, "message": {"type": "string"}}}]}, "message": {"type": "string"}, "code": {"type": "string"}}},
            },
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
