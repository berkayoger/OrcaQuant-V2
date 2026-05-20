from app.extensions import db
from app.factory import create_app
from app.models.api_key import ApiKey
from app.models.audit_event import AuditEvent
from app.models.payment import PaymentTransaction
from app.models.plan import Plan
from app.models.promo_code import PromoCode
from app.models.session import Session
from app.models.usage import DailyUsage, FeatureLimit
from app.models.user import User


def test_critical_models_registered_in_metadata():
    app = create_app("testing")
    with app.app_context():
        db.drop_all()
        db.create_all()
        table_names = set(db.metadata.tables.keys())

    expected = {
        User.__tablename__,
        Session.__tablename__,
        ApiKey.__tablename__,
        Plan.__tablename__,
        FeatureLimit.__tablename__,
        DailyUsage.__tablename__,
        PaymentTransaction.__tablename__,
        PromoCode.__tablename__,
        AuditEvent.__tablename__,
    }
    assert expected.issubset(table_names)
