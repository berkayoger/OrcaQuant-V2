from flask import Blueprint, jsonify


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/")
def get_dashboard_status():
    return jsonify({"module": "dashboard", "status": "not_implemented"}), 200
