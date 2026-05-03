from flask import Blueprint, jsonify


admin_user_bp = Blueprint("admin_users", __name__)


@admin_user_bp.get("/")
def get_admin_users_status():
    return jsonify({"module": "admin_users", "status": "not_implemented"}), 200
