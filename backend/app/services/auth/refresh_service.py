import hashlib

from app.core.errors.exceptions import AuthenticationError
from app.core.security.token_service import create_access_token, decode_refresh_token
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository


class RefreshService:
    def __init__(self, session_repository: SessionRepository | None = None, user_repository: UserRepository | None = None) -> None:
        self.session_repository = session_repository or SessionRepository()
        self.user_repository = user_repository or UserRepository()

    def execute(self, refresh_token: str) -> dict:
        payload = decode_refresh_token(refresh_token)
        jti = payload.get("jti")
        if not jti:
            raise AuthenticationError("Invalid refresh token")
        session = self.session_repository.get_active_by_jti(jti)
        if not session:
            raise AuthenticationError("Session is not active")
        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        if session.refresh_token_hash != token_hash:
            raise AuthenticationError("Session token mismatch")
        user = self.user_repository.get_by_id(payload["sub"])
        if not user or not user.get("is_active"):
            raise AuthenticationError("Invalid user")
        access_token = create_access_token(subject=user["id"], claims={"email": user["email"], "role": user["role"]})
        # TODO(v1-migration): implement refresh token rotation and reuse-detection hardening.
        return {"access_token": access_token, "token_type": "bearer", "user": {"id": user["id"], "email": user["email"], "role": user["role"], "plan_code": user.get("plan_code")}}
