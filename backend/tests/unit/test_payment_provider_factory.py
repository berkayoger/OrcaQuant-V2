from app.payments.fake_provider import FakePaymentProvider
from app.payments.iyzico_provider import IyzicoProvider
from app.payments.provider_factory import get_payment_provider


def test_payment_provider_factory_defaults_to_fake(app):
    with app.app_context():
        app.config["BILLING_PROVIDER"] = "fake"
        assert isinstance(get_payment_provider(), FakePaymentProvider)


def test_payment_provider_factory_iyzico(app):
    with app.app_context():
        app.config["BILLING_PROVIDER"] = "iyzico"
        assert isinstance(get_payment_provider(), IyzicoProvider)
