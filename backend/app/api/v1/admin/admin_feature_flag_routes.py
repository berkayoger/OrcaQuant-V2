from flask import Blueprint, jsonify


admin_feature_flag_bp = Blueprint("admin_feature_flags", __name__)


@admin_feature_flag_bp.get("/")
def get_admin_feature_flags_status():
    return jsonify({"module": "admin_feature_flags", "status": "not_implemented"}), 200
