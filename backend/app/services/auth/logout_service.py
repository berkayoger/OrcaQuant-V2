from app.repositories.session_repository import SessionRepository


class LogoutService:
    def __init__(self, repository: SessionRepository | None = None):
        self.repository = repository or SessionRepository()

    def execute(self, jti: str) -> bool:
        session = self.repository.get_active_by_jti(jti)
        if not session:
            return False
        self.repository.revoke(session)
        return True
