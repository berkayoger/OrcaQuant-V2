from __future__ import annotations

from pydantic import ValidationError as PydanticValidationError

from app.core.errors.exceptions import ValidationError
from app.core.security.password_hasher import hash_password
from app.core.security.token_service import create_access_token
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import AuthResponse, RegisterRequest


class RegisterService:
    def __init__(self, user_repository: UserRepository | None = None) -> None:
        self.user_repository = user_repository or UserRepository()

    def execute(self, payload: dict) -> dict:
        try:
            request = RegisterRequest.model_validate(payload)
        except PydanticValidationError as exc:
            raise ValidationError("Invalid registration payload") from exc

        password_hash = hash_password(request.password)
        user = self.user_repository.create_user(email=str(request.email), password_hash=password_hash)
        access_token = create_access_token(subject=user["id"], claims={"email": user["email"], "role": user["role"]})
        response = AuthResponse(access_token=access_token, user_id=user["id"], email=user["email"])
        return response.model_dump()
