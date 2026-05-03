from flask import Blueprint, jsonify


admin_limit_bp = Blueprint("admin_limits", __name__)


@admin_limit_bp.get("/")
def get_admin_limits_status():
    return jsonify({"module": "admin_limits", "status": "not_implemented"}), 200
