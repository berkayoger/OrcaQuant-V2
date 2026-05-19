from app.factory import create_app
from app.models import User, Session, ApiKey, Plan, FeatureLimit, DailyUsage, PaymentTransaction, PromoCode, AuditEvent


def test_create_app_testing_imports():
    app = create_app("testing")
    assert app.testing is True


def test_models_registered(app):
    with app.app_context():
        assert User.__tablename__ in {"users"}
        assert Session.__tablename__ == "sessions"
        assert ApiKey.__tablename__
        assert Plan.__tablename__
        assert FeatureLimit.__tablename__
        assert DailyUsage.__tablename__
        assert PaymentTransaction.__tablename__
        assert PromoCode.__tablename__
        assert AuditEvent.__tablename__
