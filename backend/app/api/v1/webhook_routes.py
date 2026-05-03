from flask import Blueprint, jsonify


webhook_bp = Blueprint("webhooks", __name__)


@webhook_bp.get("/")
def get_webhooks_status():
    return jsonify({"module": "webhooks", "status": "not_implemented"}), 200
