from flask import Blueprint, jsonify


profile_bp = Blueprint("profile", __name__)


@profile_bp.get("/")
def get_profile_status():
    return jsonify({"module": "profile", "status": "not_implemented"}), 200
