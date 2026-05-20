from flask import Blueprint, current_app, jsonify

from app.core.security.auth_guard import require_auth

billing_bp = Blueprint("billing", __name__)


@billing_bp.get("/status")
def get_billing_status():
    enabled = bool(current_app.config.get("ENABLE_BILLING", False))
    return jsonify({"module": "billing", "enabled": enabled, "status": "not_implemented" if enabled else "disabled"}), 200


@billing_bp.post("/initiate")
@require_auth
def initiate_billing():
    enabled = bool(current_app.config.get("ENABLE_BILLING", False))
    if not enabled:
        return jsonify({"code": "billing_disabled", "message": "Billing is disabled"}), 501
    return jsonify({"code": "not_implemented", "message": "TODO(v1-migration): implement iyzico verification and transaction idempotency"}), 501
