from app.models.plan import Plan
from app.models.usage import FeatureLimit
from app.models.user import User
from app.extensions import db
from app.services.usage.usage_service import UsageService


def test_usage_increment(app):
    with app.app_context():
        plan = Plan(code="free", name="Free")
        db.session.add(plan)
        db.session.flush()
        db.session.add(FeatureLimit(plan_id=plan.id, feature_key="technical_analysis", daily_quota=3, enabled=True))
        user = User(email="u1@example.com", password_hash="x", plan_id=plan.id)
        db.session.add(user)
        db.session.commit()

        svc = UsageService()
        s1 = svc.check_limit(user.id, "technical_analysis", plan.id)
        assert s1["used"] == 0 and s1["quota"] == 3
        s2 = svc.increment(user.id, "technical_analysis", plan.id)
        assert s2["used"] == 1 and s2["remaining"] == 2
