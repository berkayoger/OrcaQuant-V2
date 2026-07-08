from flask import Blueprint, jsonify


webhook_bp = Blueprint("webhooks", __name__)


@webhook_bp.get("/")
def get_webhooks_status():
    return jsonify(
        {
            "module": "webhooks",
            "status": "ready_for_provider_binding",
            "boundaries": {
                "billing_callback": "/api/v1/billing/callback/{provider_name}",
                "iyzico_compat_callback": "/api/v1/billing/callback/iyzico",
            },
            "note": "Provider-specific signature verification stays inside each adapter.",
        }
    ), 200
