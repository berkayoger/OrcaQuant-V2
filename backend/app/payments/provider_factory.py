from __future__ import annotations

from flask import current_app

from app.payments.fake_provider import FakePaymentProvider
from app.payments.iyzico_provider import IyzicoProvider
from app.payments.provider_base import PaymentProvider, ProviderCapabilities, ProviderReadiness

_PROVIDER_REGISTRY: dict[str, type[PaymentProvider]] = {
    FakePaymentProvider.name: FakePaymentProvider,
    IyzicoProvider.name: IyzicoProvider,
}


def supported_payment_providers() -> list[str]:
    return sorted(_PROVIDER_REGISTRY)


def get_payment_provider(provider_name: str | None = None) -> PaymentProvider:
    name = (provider_name or current_app.config.get("BILLING_PROVIDER", "fake")).strip().lower()
    provider_cls = _PROVIDER_REGISTRY.get(name)
    if provider_cls is None:
        supported = ", ".join(supported_payment_providers())
        raise ValueError(f"Unsupported billing provider '{name}'. Supported providers: {supported}")
    return provider_cls()


def get_provider_readiness(provider_name: str | None = None) -> ProviderReadiness:
    provider = get_payment_provider(provider_name)
    readiness = getattr(provider, "readiness", None)
    if callable(readiness):
        return readiness()
    return ProviderReadiness(
        name=provider.name,
        configured=False,
        mode="unknown",
        missing_settings=[],
        capabilities=ProviderCapabilities(hosted_checkout=False, webhook_verification=False),
        integration_status="readiness_not_implemented",
    )


def list_provider_readiness() -> list[dict]:
    return [get_provider_readiness(name).to_dict() for name in supported_payment_providers()]
