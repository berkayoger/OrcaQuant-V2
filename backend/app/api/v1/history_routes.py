from flask import Blueprint, jsonify


history_bp = Blueprint("history", __name__)


@history_bp.get("/")
def get_history_status():
    return jsonify({"module": "history", "status": "not_implemented"}), 200
