from datetime import UTC, datetime

from app.extensions import db
from app.models.session import Session


class SessionRepository:
    def create(self, **kwargs) -> Session:
        session = Session(**kwargs)
        db.session.add(session)
        db.session.commit()
        return session

    def get_active_by_jti(self, jti: str) -> Session | None:
        return Session.query.filter_by(jti=jti, is_active=True).first()

    def revoke_by_jti(self, jti: str) -> bool:
        session = self.get_active_by_jti(jti)
        if not session:
            return False
        session.is_active = False
        session.revoked_at = datetime.now(UTC)
        db.session.commit()
        return True

    def revoke_all_for_user(self, user_id: str) -> int:
        sessions = Session.query.filter_by(user_id=user_id, is_active=True).all()
        now = datetime.now(UTC)
        for session in sessions:
            session.is_active = False
            session.revoked_at = now
        db.session.commit()
        return len(sessions)
