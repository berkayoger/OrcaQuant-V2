from flask import Blueprint, jsonify


admin_system_bp = Blueprint("admin_system", __name__)


@admin_system_bp.get("/")
def get_admin_system_status():
    return jsonify({"module": "admin_system", "status": "not_implemented"}), 200
