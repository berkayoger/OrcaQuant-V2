from __future__ import annotations

from app.payments.provider_base import (
    PaymentProvider,
    ProviderInitiateRequest,
    ProviderInitiateResponse,
    ProviderVerificationResult,
)


class FakePaymentProvider(PaymentProvider):
    name = "fake"

    def initiate_payment(self, request: ProviderInitiateRequest) -> ProviderInitiateResponse:
        conversation_id = f"fake-conv-{request.transaction_id}"
        payment_id = f"fake-pay-{request.transaction_id}"
        return ProviderInitiateResponse(
            provider_payment_id=payment_id,
            provider_conversation_id=conversation_id,
            checkout_url=f"https://fake-billing.local/checkout/{conversation_id}",
            raw_payload={"provider": self.name, "conversationId": conversation_id, "paymentId": payment_id},
        )

    def verify_callback(self, payload: dict, signature: str | None) -> ProviderVerificationResult:
        verified = bool(payload.get("mock_verified") is True)
        provider_status = str(payload.get("paymentStatus", "failed")).lower()
        status = "paid" if verified and provider_status in {"paid", "success"} else "failed"
        return ProviderVerificationResult(
            is_verified=verified,
            status=status,
            provider_payment_id=payload.get("paymentId"),
            provider_conversation_id=payload.get("conversationId"),
            raw_payload=payload,
            failure_reason=None if verified else "fake_verification_failed",
        )
