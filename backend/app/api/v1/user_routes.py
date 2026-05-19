from flask import Blueprint, jsonify, request

from app.services.usage.usage_service import UsageService


user_bp = Blueprint("user", __name__)


@user_bp.get("/")
def get_user_status():
    return jsonify({"module": "user", "status": "not_implemented"}), 200


@user_bp.get("/usage")
def get_usage_status():
    user_id = request.args.get("user_id", "")
    feature_key = request.args.get("feature_key", "technical_analysis")
    if not user_id:
        return jsonify({"code": "missing_user_id"}), 400
    return jsonify(UsageService().get_status(user_id, feature_key)), 200
