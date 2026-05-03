from __future__ import annotations

from pydantic import ValidationError as PydanticValidationError

from app.core.errors.exceptions import AuthenticationError, ValidationError
from app.core.security.password_hasher import verify_password
from app.core.security.token_service import create_access_token
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import AuthResponse, LoginRequest


class LoginService:
    def __init__(self, user_repository: UserRepository | None = None) -> None:
        self.user_repository = user_repository or UserRepository()

    def execute(self, payload: dict) -> dict:
        try:
            request = LoginRequest.model_validate(payload)
        except PydanticValidationError as exc:
            raise ValidationError("Invalid login payload") from exc

        user = self.user_repository.get_by_email(str(request.email))
        if not user or not verify_password(request.password, user["password_hash"]):
            raise AuthenticationError("Invalid email or password")

        access_token = create_access_token(subject=user["id"], claims={"email": user["email"], "role": user["role"]})
        response = AuthResponse(access_token=access_token, user_id=user["id"], email=user["email"])
        return response.model_dump()
