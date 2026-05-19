import hashlib
from datetime import UTC, datetime, timedelta

from app.repositories.session_repository import SessionRepository


class SessionService:
    def __init__(self, repository: SessionRepository | None = None):
        self.repository = repository or SessionRepository()

    def create_refresh_session(self, user_id: str, refresh_token: str, jti: str, days: int = 7, user_agent: str | None = None, ip_address: str | None = None):
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        return self.repository.create(
            user_id=user_id,
            refresh_token_hash=token_hash,
            jti=jti,
            user_agent=user_agent,
            ip_address=ip_address,
            expires_at=datetime.now(UTC) + timedelta(days=days),
        )
