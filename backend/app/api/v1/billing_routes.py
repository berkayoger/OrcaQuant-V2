from flask import Blueprint, jsonify


billing_bp = Blueprint("billing", __name__)


@billing_bp.get("/")
def get_billing_status():
    return jsonify({"module": "billing", "status": "not_implemented"}), 200
