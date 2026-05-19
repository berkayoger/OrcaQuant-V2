import hashlib
import secrets

from app.repositories.api_key_repository import ApiKeyRepository


class ApiKeyService:
    def __init__(self, repository: ApiKeyRepository | None = None):
        self.repository = repository or ApiKeyRepository()

    def create_key(self, user_id: str, name: str) -> dict:
        raw = f"oq_{secrets.token_urlsafe(24)}"
        self.repository.create(user_id=user_id, name=name, key_hash=hashlib.sha256(raw.encode()).hexdigest())
        return {"api_key": raw, "name": name}
