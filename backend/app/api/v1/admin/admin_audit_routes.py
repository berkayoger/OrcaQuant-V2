from flask import Blueprint, jsonify


admin_audit_bp = Blueprint("admin_audit_logs", __name__)


@admin_audit_bp.get("/")
def get_admin_audit_logs_status():
    return jsonify({"module": "admin_audit_logs", "status": "not_implemented"}), 200
