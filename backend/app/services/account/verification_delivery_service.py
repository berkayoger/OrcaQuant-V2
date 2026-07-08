from __future__ import annotations

from flask import current_app


class VerificationDeliveryService:
    """Delivery boundary for account verification codes.

    A real email/SMS provider should be wired here later. Until then, the
    service records the delivery contract and only exposes the raw code in
    debug/test mode so automated tests and local development stay usable.
    """

    def deliver(self, *, email: str, code: str, purpose: str) -> dict:
        channel = str(current_app.config.get("ACCOUNT_CODE_CHANNEL", "email")).lower()
        payload = {
            "channel": channel,
            "status": "queued",
            "provider": "not_configured",
            "target": email,
            "purpose": purpose,
        }
        if current_app.config.get("ACCOUNT_CODE_DEBUG_RESPONSE") or current_app.config.get("TESTING") or current_app.config.get("DEBUG"):
            payload["debug_code"] = code
            payload["provider"] = "debug_response"
            payload["status"] = "delivered_debug"
        return payload
