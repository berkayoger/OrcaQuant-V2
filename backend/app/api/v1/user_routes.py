from flask import Blueprint, g, jsonify, request

from app.core.security.auth_guard import require_auth
from app.models.plan import Plan
from app.services.usage.usage_service import UsageService


user_bp = Blueprint("user", __name__)


@user_bp.get("/")
@require_auth
def get_user_status():
    plan = Plan.query.filter_by(id=g.current_user.plan_id).one_or_none() if g.current_user.plan_id else None
    return jsonify({
        "id": g.current_user.id,
        "email": g.current_user.email,
        "role": g.current_user.role,
        "plan_code": plan.code if plan else None,
        "subscription_status": g.current_user.subscription_status,
    }), 200


@user_bp.get("/usage")
@require_auth
def get_usage_status():
    feature_key = request.args.get("feature_key", "technical_analysis")
    return jsonify(UsageService().get_status(g.current_user.id, feature_key, g.current_user.plan_id)), 200
