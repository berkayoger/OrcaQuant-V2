from flask import Blueprint, g, jsonify, request

from app.core.security.auth_guard import require_auth
from app.services.usage.usage_service import UsageService


user_bp = Blueprint("user", __name__)


@user_bp.get("/")
@require_auth
def get_user_status():
    return jsonify({"module": "user", "status": "ready", "user_id": g.current_user.id}), 200


@user_bp.get("/usage")
@require_auth
def get_usage_status():
    feature_key = request.args.get("feature_key", "technical_analysis")
    return jsonify(UsageService().get_status(g.current_user.id, feature_key, g.current_user.plan_id)), 200
