from flask import Blueprint, jsonify


admin_security_bp = Blueprint("admin_security", __name__)


@admin_security_bp.get("/")
def get_admin_security_status():
    return jsonify({"module": "admin_security", "status": "not_implemented"}), 200
