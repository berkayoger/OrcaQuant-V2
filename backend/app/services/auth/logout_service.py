from app.repositories.session_repository import SessionRepository
from app.core.errors.exceptions import AuthenticationError


class LogoutService:
    def __init__(self, repository: SessionRepository | None = None):
        self.repository = repository or SessionRepository()

    def execute(self, jti: str) -> bool:
        if not self.repository.revoke_by_jti(jti):
            raise AuthenticationError("Session is not active")
        return True
