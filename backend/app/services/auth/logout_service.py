from app.repositories.session_repository import SessionRepository


class LogoutService:
    def __init__(self, repository: SessionRepository | None = None):
        self.repository = repository or SessionRepository()

    def execute(self, jti: str) -> bool:
        return self.repository.revoke_by_jti(jti)
