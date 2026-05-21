from __future__ import annotations

from flask import current_app

from app.payments.fake_provider import FakePaymentProvider
from app.payments.iyzico_provider import IyzicoProvider
from app.payments.provider_base import PaymentProvider


def get_payment_provider(provider_name: str | None = None) -> PaymentProvider:
    name = (provider_name or current_app.config.get("BILLING_PROVIDER", "fake")).lower()
    if name == "iyzico":
        return IyzicoProvider()
    return FakePaymentProvider()
