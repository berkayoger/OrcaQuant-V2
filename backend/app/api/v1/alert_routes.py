from flask import Blueprint, jsonify


alert_bp = Blueprint("alerts", __name__)


@alert_bp.get("/")
def get_alerts_status():
    return jsonify({"module": "alerts", "status": "not_implemented"}), 200
