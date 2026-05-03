from flask import Blueprint, jsonify


admin_engine_bp = Blueprint("admin_engines", __name__)


@admin_engine_bp.get("/")
def get_admin_engines_status():
    return jsonify({"module": "admin_engines", "status": "not_implemented"}), 200
