from app.core.errors.exceptions import AuthenticationError
from app.core.errors import error_codes
from app.core.security.token_service import create_access_token, create_refresh_token, decode_refresh_token
from app.repositories.session_repository import SessionRepository
from app.repositories.user_repository import UserRepository
from app.services.auth.session_service import SessionService


class RefreshService:
    def __init__(self, session_repository: SessionRepository | None = None, user_repository: UserRepository | None = None) -> None:
        self.session_repository = session_repository or SessionRepository()
        self.user_repository = user_repository or UserRepository()
        self.session_service = SessionService(repository=self.session_repository)

    def execute(self, refresh_token: str) -> dict:
        payload = decode_refresh_token(refresh_token)
        jti = payload.get("jti")
        user_id = payload.get("sub")
        if not jti or not user_id:
            raise AuthenticationError("Invalid refresh token", error_code=error_codes.TOKEN_INVALID_ERROR)
        session = self.session_repository.get_by_jti(jti)
        if not session:
            raise AuthenticationError("Session is not active")
        if not session.is_active:
            self.session_service.revoke_all_user_sessions(session.user_id)
            raise AuthenticationError("Refresh token reuse detected", error_code="refresh_token_reuse_detected")
        if not self.session_repository.is_token_hash_match(session, refresh_token):
            self.session_service.revoke_all_user_sessions(session.user_id)
            raise AuthenticationError("Refresh token mismatch", error_code="refresh_token_mismatch")
        user = self.user_repository.get_by_id(user_id)
        if not user or not user.get("is_active"):
            self.session_service.revoke_session(jti)
            raise AuthenticationError("Invalid user")
        access_token = create_access_token(subject=user["id"], claims={"email": user["email"], "role": user["role"]})
        new_refresh_token, new_jti = create_refresh_token(user["id"])
        self.session_service.rotate_refresh_session(old_jti=jti, user_id=user["id"], new_refresh_token=new_refresh_token, new_jti=new_jti)
        return {"access_token": access_token, "refresh_token": new_refresh_token, "token_type": "bearer", "user": {"id": user["id"], "email": user["email"], "role": user["role"], "plan_code": user.get("plan_code")}}
