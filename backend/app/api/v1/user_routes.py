from flask import Blueprint, jsonify


user_bp = Blueprint("user", __name__)


@user_bp.get("/")
def get_user_status():
    return jsonify({"module": "user", "status": "not_implemented"}), 200
