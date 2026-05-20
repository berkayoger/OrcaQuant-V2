import hashlib
from datetime import UTC, datetime, timedelta

from flask import current_app
from app.extensions import db

from app.repositories.session_repository import SessionRepository


class SessionService:
    def __init__(self, repository: SessionRepository | None = None):
        self.repository = repository or SessionRepository()

    def create_refresh_session(self, user_id: str, refresh_token: str, jti: str, user_agent: str | None = None, ip_address: str | None = None):
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        days = int(current_app.config.get("JWT_REFRESH_TOKEN_DAYS", 7))
        return self.repository.create_session(
            user_id=user_id,
            refresh_token_hash=token_hash,
            jti=jti,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=datetime.now(UTC) + timedelta(days=days),
        )

    def rotate_refresh_session(self, old_jti: str, user_id: str, new_refresh_token: str, new_jti: str):
        token_hash = hashlib.sha256(new_refresh_token.encode()).hexdigest()
        days = int(current_app.config.get("JWT_REFRESH_TOKEN_DAYS", 7))
        now = datetime.now(UTC)
        old_session = self.repository.get_active_by_jti(old_jti)
        if old_session:
            old_session.is_active = False
            old_session.revoked_at = now
        new_session = self.repository.create(
            user_id=user_id,
            refresh_token_hash=token_hash,
            jti=new_jti,
            expires_at=now + timedelta(days=days),
            is_active=True,
        )
        db.session.commit()
        return new_session

    def revoke_session(self, jti: str) -> bool:
        return self.repository.revoke_by_jti(jti)

    def revoke_all_user_sessions(self, user_id: str) -> int:
        return self.repository.revoke_all_for_user(user_id)
