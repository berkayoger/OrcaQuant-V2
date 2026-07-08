from __future__ import annotations

from dataclasses import dataclass, field
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
    customer_email: str | None = None
    success_url: str | None = None
    failure_url: str | None = None
    callback_url: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)


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


@dataclass(frozen=True)
class ProviderCapabilities:
    hosted_checkout: bool
    webhook_verification: bool
    refunds: bool = False
    subscriptions: bool = False

    def to_dict(self) -> dict:
        return {
            "hosted_checkout": self.hosted_checkout,
            "webhook_verification": self.webhook_verification,
            "refunds": self.refunds,
            "subscriptions": self.subscriptions,
        }


@dataclass(frozen=True)
class ProviderReadiness:
    name: str
    configured: bool
    mode: str
    missing_settings: list[str]
    capabilities: ProviderCapabilities
    integration_status: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "configured": self.configured,
            "mode": self.mode,
            "missing_settings": self.missing_settings,
            "capabilities": self.capabilities.to_dict(),
            "integration_status": self.integration_status,
        }


class PaymentProvider(Protocol):
    name: str

    def initiate_payment(self, request: ProviderInitiateRequest) -> ProviderInitiateResponse:
        ...

    def verify_callback(self, payload: dict, signature: str | None) -> ProviderVerificationResult:
        ...
