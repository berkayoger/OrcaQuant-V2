"""Iyzico provider skeleton with explicit verification boundary.

This provider intentionally does not implement cryptographic callback verification yet.
Do not mark any payment as paid unless verify_callback returns is_verified=True.
"""

from __future__ import annotations

from app.payments.provider_base import (
    PaymentProvider,
    ProviderInitiateRequest,
    ProviderInitiateResponse,
    ProviderVerificationResult,
)


class IyzicoProvider(PaymentProvider):
    name = "iyzico"

    def initiate_payment(self, request: ProviderInitiateRequest) -> ProviderInitiateResponse:
        conversation_id = f"conv-{request.transaction_id}"
        payment_id = f"pay-{request.transaction_id}"
        return ProviderInitiateResponse(
            provider_payment_id=payment_id,
            provider_conversation_id=conversation_id,
            checkout_url=f"https://sandbox-iyzico.example/checkout/{conversation_id}",
            raw_payload={
                "provider": self.name,
                "paymentId": payment_id,
                "conversationId": conversation_id,
                "note": "skeleton_response",
            },
        )

    def verify_callback(self, payload: dict, signature: str | None) -> ProviderVerificationResult:
        # Verification boundary:
        # - real HMAC/signature verification is NOT implemented in this migration step.
        # - only explicitly mocked tests should treat callbacks as verified.
        verified = bool(payload.get("mock_verified") is True and signature == "valid-test-signature")
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
