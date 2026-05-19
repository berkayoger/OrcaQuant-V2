from flask import Blueprint, current_app, jsonify

billing_bp = Blueprint("billing", __name__)


@billing_bp.get("/status")
def get_billing_status():
    enabled = bool(current_app.config.get("ENABLE_BILLING", False))
    return jsonify({"module": "billing", "enabled": enabled, "status": "ready" if enabled else "not_implemented"}), 200


@billing_bp.post("/initiate")
def initiate_billing():
    enabled = bool(current_app.config.get("ENABLE_BILLING", False))
    if not enabled:
        return jsonify({"code": "not_implemented", "message": "Billing disabled"}), 501
    return jsonify({"code": "not_implemented", "message": "TODO(v1-migration): provider integration"}), 501
