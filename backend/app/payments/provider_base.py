from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol


@dataclass(frozen=True)
class ProviderInitiateRequest:
    transaction_id: str
    user_id: str
    plan_code: str
    amount: Decimal
    currency: str
    idempotency_key: str


@dataclass(frozen=True)
class ProviderInitiateResponse:
    provider_payment_id: str
    provider_conversation_id: str
    checkout_url: str
    raw_payload: dict


@dataclass(frozen=True)
class ProviderVerificationResult:
    is_verified: bool
    status: str
    provider_payment_id: str | None
    provider_conversation_id: str | None
    raw_payload: dict
    failure_reason: str | None = None


class PaymentProvider(Protocol):
    name: str

    def initiate_payment(self, request: ProviderInitiateRequest) -> ProviderInitiateResponse:
        ...

    def verify_callback(self, payload: dict, signature: str | None) -> ProviderVerificationResult:
        ...
