from app.extensions import db
from app.models.plan import Plan


def test_plan_can_be_created(app):
    with app.app_context():
        plan = Plan(code="free", name="Free")
        db.session.add(plan)
        db.session.commit()
        assert plan.id is not None
        assert plan.is_active is True
        assert plan.sort_order == 0
