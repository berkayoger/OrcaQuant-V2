"""Iyzico provider adapter boundary.

The app is now ready to route payment initiation and callbacks through this
adapter, but the outbound Iyzico SDK/API call is intentionally isolated here.
When credentials and the concrete checkout client are selected, only this file
should need the external HTTP/SDK binding.
"""

from __future__ import annotations

from flask import current_app, has_app_context

from app.payments.provider_base import (
    PaymentProvider,
    ProviderCapabilities,
    ProviderInitiateRequest,
    ProviderInitiateResponse,
    ProviderReadiness,
    ProviderVerificationResult,
)

_PLACEHOLDER_VALUES = {"", "placeholder", "change-me", "set-me", "todo"}
_REQUIRED_SETTINGS = ["IYZICO_API_KEY", "IYZICO_SECRET", "IYZICO_BASE_URL"]


class IyzicoProvider(PaymentProvider):
    name = "iyzico"

    def readiness(self) -> ProviderReadiness:
        missing = self._missing_settings()
        return ProviderReadiness(
            name=self.name,
            configured=not missing,
            mode=self._mode(),
            missing_settings=missing,
            capabilities=ProviderCapabilities(hosted_checkout=True, webhook_verification=True),
            integration_status="adapter_ready_provider_call_pending" if not missing else "waiting_for_credentials",
        )

    def initiate_payment(self, request: ProviderInitiateRequest) -> ProviderInitiateResponse:
        missing = self._missing_settings()
        if missing:
            raise RuntimeError(f"Iyzico provider is not configured. Missing: {', '.join(missing)}")

        conversation_id = f"iyzico-conv-{request.transaction_id}"
        payment_id = f"iyzico-pay-{request.transaction_id}"
        checkout_url = f"{self._config('IYZICO_BASE_URL').rstrip('/')}/checkout/{conversation_id}"
        return ProviderInitiateResponse(
            provider_payment_id=payment_id,
            provider_conversation_id=conversation_id,
            checkout_url=checkout_url,
            raw_payload={
                "provider": self.name,
                "integrationStatus": "adapter_ready_provider_call_pending",
                "conversationId": conversation_id,
                "paymentId": payment_id,
                "checkoutUrl": checkout_url,
                "request": {
                    "transactionId": request.transaction_id,
                    "userId": request.user_id,
                    "customerEmail": request.customer_email,
                    "planCode": request.plan_code,
                    "amount": str(request.amount),
                    "currency": request.currency,
                    "successUrl": request.success_url,
                    "failureUrl": request.failure_url,
                    "callbackUrl": request.callback_url,
                    "metadata": request.metadata,
                },
                "bindingBoundary": "Replace the skeleton checkout payload with the real Iyzico SDK/API call here.",
            },
        )

    def verify_callback(self, payload: dict, signature: str | None) -> ProviderVerificationResult:
        # Verification boundary:
        # - real HMAC/signature verification stays isolated in this adapter.
        # - mocked verification is allowed only outside production/test wiring.
        allow_mock = bool(current_app.config.get("TESTING", False) or current_app.config.get("DEBUG", False)) if has_app_context() else False
        verified = bool(allow_mock and payload.get("mock_verified") is True and signature == "valid-test-signature")
        provider_status = str(payload.get("paymentStatus", "failed")).lower()

        mapped_status = "failed"
        if verified and provider_status in {"paid", "success"}:
            mapped_status = "paid"
        elif provider_status in {"cancelled", "canceled"}:
            mapped_status = "cancelled"
        elif provider_status in {"pending", "processing"}:
            mapped_status = "pending"

        return ProviderVerificationResult(
            is_verified=verified,
            status=mapped_status,
            provider_payment_id=payload.get("paymentId"),
            provider_conversation_id=payload.get("conversationId"),
            raw_payload=payload,
            failure_reason=None if verified else "callback_signature_not_verified",
        )

    @staticmethod
    def _config(key: str) -> str:
        if not has_app_context():
            return ""
        return str(current_app.config.get(key) or "").strip()

    @classmethod
    def _missing_settings(cls) -> list[str]:
        return [key for key in _REQUIRED_SETTINGS if cls._config(key).lower() in _PLACEHOLDER_VALUES]

    @classmethod
    def _mode(cls) -> str:
        base_url = cls._config("IYZICO_BASE_URL").lower()
        if "sandbox" in base_url:
            return "sandbox"
        return "production"
