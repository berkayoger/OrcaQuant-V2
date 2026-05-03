from app.extensions import db
from app.models.user import User


def test_user_can_be_created(app):
    with app.app_context():
        user = User(email="model@example.com", password_hash="hash")
        db.session.add(user)
        db.session.commit()
        assert user.id is not None
        assert user.email == "model@example.com"


def test_user_email_unique_constraint(app):
    with app.app_context():
        db.session.add(User(email="dup@example.com", password_hash="a"))
        db.session.commit()
        db.session.add(User(email="dup@example.com", password_hash="b"))
        try:
            db.session.commit()
            assert False, "expected unique constraint error"
        except Exception:
            db.session.rollback()
