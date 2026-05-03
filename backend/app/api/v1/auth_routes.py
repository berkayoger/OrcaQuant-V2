from flask import Blueprint, jsonify


auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/")
def get_auth_status():
    return jsonify({"module": "auth", "status": "not_implemented"}), 200
