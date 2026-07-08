from datetime import UTC, datetime
import hashlib

from app.extensions import db
from app.models.session import Session


class SessionRepository:
    def create(self, **kwargs) -> Session:
        session = Session(**kwargs)
        db.session.add(session)
        db.session.commit()
        return session

    def create_session(self, user_id: str, refresh_token_hash: str, jti: str, expires_at: datetime, user_agent: str | None = None, ip_address: str | None = None) -> Session:
        return self.create(
            user_id=user_id,
            refresh_token_hash=refresh_token_hash,
            jti=jti,
            expires_at=expires_at,
            user_agent=user_agent,
            ip_address=ip_address,
            is_active=True,
        )

    def get_by_jti(self, jti: str) -> Session | None:
        return Session.query.filter_by(jti=jti).first()

    def get_active_by_jti(self, jti: str) -> Session | None:
        return Session.query.filter_by(jti=jti, is_active=True).first()

    def list_for_user(self, user_id: str) -> list[Session]:
        return Session.query.filter_by(user_id=user_id).order_by(Session.created_at.desc()).all()

    def revoke_by_id_for_user(self, session_id: str, user_id: str) -> bool:
        session = Session.query.filter_by(id=session_id, user_id=user_id, is_active=True).one_or_none()
        if not session:
            return False
        session.is_active = False
        session.revoked_at = datetime.now(UTC)
        db.session.commit()
        return True

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

    def is_token_hash_match(self, session: Session, raw_refresh_token: str) -> bool:
        token_hash = hashlib.sha256(raw_refresh_token.encode()).hexdigest()
        return session.refresh_token_hash == token_hash
