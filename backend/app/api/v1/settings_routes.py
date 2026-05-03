from flask import Blueprint, jsonify


settings_bp = Blueprint("settings", __name__)


@settings_bp.get("/")
def get_settings_status():
    return jsonify({"module": "settings", "status": "not_implemented"}), 200
