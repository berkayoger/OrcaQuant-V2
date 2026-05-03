from app.extensions import db
from app.models.usage_event import UsageEvent
from app.models.user import User


def test_usage_event_can_be_created(app):
    with app.app_context():
        user = User(email="usage@example.com", password_hash="hash")
        db.session.add(user)
        db.session.commit()
        event = UsageEvent(user_id=user.id, feature="analysis.run")
        db.session.add(event)
        db.session.commit()
        assert event.id is not None
        assert event.amount == 1
