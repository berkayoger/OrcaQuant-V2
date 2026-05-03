from flask import Blueprint, jsonify


admin_dashboard_bp = Blueprint("admin_dashboard", __name__)


@admin_dashboard_bp.get("/")
def get_admin_dashboard_status():
    return jsonify({"module": "admin_dashboard", "status": "not_implemented"}), 200
