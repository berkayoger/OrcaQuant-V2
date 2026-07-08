from pydantic import ValidationError as PydanticValidationError
from flask import Blueprint, jsonify, request

from app.core.errors.exceptions import ValidationError
from app.core.security.password_hasher import hash_password
from app.core.security.token_service import create_access_token, create_refresh_token, decode_refresh_token
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import EmailCodeRequest, PasswordResetRequest, SendVerificationCodeRequest, VerifyCodeRequest
from app.services.account.username_service import UsernameService
from app.services.account.verification_code_service import AccountVerificationCodeService
from app.services.auth.login_service import LoginService
from app.services.auth.logout_service import LogoutService
from app.services.auth.refresh_service import RefreshService
from app.services.auth.register_service import RegisterService
from app.services.auth.session_service import SessionService


auth_bp = Blueprint("auth", __name__)
_user_repo = UserRepository()
_register_service = RegisterService(user_repository=_user_repo)
_login_service = LoginService(user_repository=_user_repo)
_refresh_service = RefreshService(user_repository=_user_repo)
_logout_service = LogoutService()
_session_service = SessionService()
_verification_service = AccountVerificationCodeService()
_username_service = UsernameService()


@auth_bp.get("/status")
def get_auth_status():
    return jsonify({"module": "auth", "status": "ok"}), 200


def _create_session_from_response(result: dict) -> None:
    user_id = result.get("user", {}).get("id")
    refresh_token = result.get("refresh_token")
    if not user_id or not refresh_token:
        return
    payload = decode_refresh_token(refresh_token)
    _session_service.create_refresh_session(user_id=user_id, refresh_token=refresh_token, jti=payload["jti"])


def _auth_response_for_user(user: User) -> dict:
    user_dict = _user_repo._to_dict(user)
    access_token = create_access_token(
        subject=user.id,
        claims={"email": user.email, "role": user.role, "token_version": user.token_version},
    )
    refresh_token, _ = create_refresh_token(user.id)
    response = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user_dict["id"],
            "email": user_dict["email"],
            "username": user_dict.get("username"),
            "role": user_dict["role"],
            "plan_code": user_dict.get("plan_code"),
            "is_email_verified": user_dict.get("is_email_verified"),
        },
    }
    _create_session_from_response(response)
    return response


@auth_bp.get("/username/check")
def check_username_availability():
    username = request.args.get("username", "")
    return jsonify(_username_service.availability(username)), 200


@auth_bp.post("/register")
def register():
    payload = request.get_json(silent=True) or {}
    result = _register_service.execute(payload)
    _create_session_from_response(result)
    return jsonify(result), 201


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    result = _login_service.execute(payload)
    _create_session_from_response(result)
    return jsonify(result), 200


@auth_bp.post("/login/code/send")
def send_login_code():
    try:
        payload = EmailCodeRequest.model_validate(request.get_json(silent=True) or {})
    except PydanticValidationError as exc:
        raise ValidationError("Invalid login code request") from exc
    result = _verification_service.send_code(email=str(payload.email), purpose=AccountVerificationCodeService.PURPOSE_LOGIN)
    return jsonify(result), 202


@auth_bp.post("/login/code")
def login_with_code():
    try:
        payload = VerifyCodeRequest.model_validate(request.get_json(silent=True) or {})
    except PydanticValidationError as exc:
        raise ValidationError("Invalid login code payload") from exc
    user = _verification_service.verify_code(email=str(payload.email), purpose=AccountVerificationCodeService.PURPOSE_LOGIN, code=payload.code)
    return jsonify(_auth_response_for_user(user)), 200


@auth_bp.post("/verification-code/send")
def send_verification_code():
    try:
        payload = SendVerificationCodeRequest.model_validate(request.get_json(silent=True) or {})
    except PydanticValidationError as exc:
        raise ValidationError("Invalid verification code request") from exc
    expose_missing = payload.purpose in {AccountVerificationCodeService.PURPOSE_EMAIL_VERIFICATION, AccountVerificationCodeService.PURPOSE_LOGIN}
    result = _verification_service.send_code(email=str(payload.email), purpose=payload.purpose, expose_missing_user=expose_missing)
    return jsonify(result), 202


@auth_bp.post("/email/verify")
def verify_email():
    try:
        payload = VerifyCodeRequest.model_validate(request.get_json(silent=True) or {})
    except PydanticValidationError as exc:
        raise ValidationError("Invalid email verification payload") from exc
    user = _verification_service.verify_code(
        email=str(payload.email),
        purpose=AccountVerificationCodeService.PURPOSE_EMAIL_VERIFICATION,
        code=payload.code,
    )
    user.is_email_verified = True
    _user_repo.mark_email_verified(user)
    return jsonify({"verified": True, "email": user.email}), 200


@auth_bp.post("/password/forgot")
def forgot_password():
    try:
        payload = EmailCodeRequest.model_validate(request.get_json(silent=True) or {})
    except PydanticValidationError as exc:
        raise ValidationError("Invalid password reset request") from exc
    result = _verification_service.send_code(
        email=str(payload.email),
        purpose=AccountVerificationCodeService.PURPOSE_PASSWORD_RESET,
        expose_missing_user=False,
    )
    result["status"] = "sent_if_account_exists"
    return jsonify(result), 202


@auth_bp.post("/password/reset")
def reset_password():
    try:
        payload = PasswordResetRequest.model_validate(request.get_json(silent=True) or {})
    except PydanticValidationError as exc:
        raise ValidationError("Invalid password reset payload") from exc
    user = _verification_service.verify_code(
        email=str(payload.email),
        purpose=AccountVerificationCodeService.PURPOSE_PASSWORD_RESET,
        code=payload.code,
    )
    _user_repo.update_password(user, hash_password(payload.new_password))
    _session_service.revoke_all_user_sessions(user.id)
    return jsonify({"reset": True}), 200


@auth_bp.post("/refresh")
def refresh():
    payload = request.get_json(silent=True) or {}
    token = payload.get("refresh_token")
    if not token:
        return jsonify({"error": {"code": "missing_refresh_token", "message": "refresh_token is required"}}), 400
    return jsonify(_refresh_service.execute(token)), 200


@auth_bp.post("/logout")
def logout():
    payload = request.get_json(silent=True) or {}
    token = payload.get("refresh_token")
    if not token:
        return jsonify({"error": {"code": "missing_refresh_token", "message": "refresh_token is required"}}), 400

    decoded = decode_refresh_token(token)
    jti = decoded.get("jti")
    if not jti:
        return jsonify({"error": {"code": "token_invalid", "message": "Invalid token"}}), 401
    _logout_service.execute(jti)
    return jsonify({"status": "ok"}), 200
