from datetime import UTC, datetime

import pytest
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.usage import DailyUsage
from app.models.user import User
from app.repositories.usage_repository import UsageRepository


def _new_user(email: str) -> User:
    user = User(email=email, password_hash="hash")
    db.session.add(user)
    db.session.commit()
    return user


def test_daily_usage_unique_user_feature_date(app):
    with app.app_context():
        user = _new_user("unique-usage@example.com")
        day = datetime.now(UTC).date()
        db.session.add(DailyUsage(user_id=user.id, feature_key="technical_analysis", usage_date=day, used_count=1))
        db.session.commit()

        db.session.add(DailyUsage(user_id=user.id, feature_key="technical_analysis", usage_date=day, used_count=1))
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()


def test_usage_repository_upsert_increment_is_stable(app):
    with app.app_context():
        user = _new_user("increment-usage@example.com")
        repo = UsageRepository()

        first = repo.upsert_increment(user.id, "technical_analysis")
        second = repo.upsert_increment(user.id, "technical_analysis")

        assert first.id == second.id
        assert second.used_count == 2
        assert DailyUsage.query.count() == 1
