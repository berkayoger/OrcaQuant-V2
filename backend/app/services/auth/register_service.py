from __future__ import annotations

from pydantic import ValidationError as PydanticValidationError

from app.core.errors.exceptions import ValidationError
from app.core.security.password_hasher import hash_password
from app.core.security.token_service import create_access_token, create_refresh_token
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import AuthResponse, RegisterRequest
from app.services.account.verification_code_service import AccountVerificationCodeService


class RegisterService:
    def __init__(self, user_repository: UserRepository | None = None, verification_service: AccountVerificationCodeService | None = None) -> None:
        self.user_repository = user_repository or UserRepository()
        self.verification_service = verification_service or AccountVerificationCodeService()

    def execute(self, payload: dict) -> dict:
        try:
            request = RegisterRequest.model_validate(payload)
        except PydanticValidationError as exc:
            raise ValidationError("Invalid registration payload") from exc

        password_hash = hash_password(request.password)
        user = self.user_repository.create_user(email=str(request.email), password_hash=password_hash, username=request.username)
        access_token = create_access_token(subject=user["id"], claims={"email": user["email"], "role": user["role"], "token_version": user["token_version"]})
        refresh_token, _ = create_refresh_token(user["id"])
        response = AuthResponse(access_token=access_token, refresh_token=refresh_token, user=user).model_dump()
        response["verification"] = self.verification_service.send_code(
            email=user["email"],
            purpose=AccountVerificationCodeService.PURPOSE_EMAIL_VERIFICATION,
        )
        return response
