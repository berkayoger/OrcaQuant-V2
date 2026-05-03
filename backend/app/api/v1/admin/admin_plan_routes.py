from flask import Blueprint, jsonify


admin_plan_bp = Blueprint("admin_plans", __name__)


@admin_plan_bp.get("/")
def get_admin_plans_status():
    return jsonify({"module": "admin_plans", "status": "not_implemented"}), 200
