from flask import Blueprint, jsonify, request

from app.core.security.token_service import decode_refresh_token
from app.repositories.user_repository import UserRepository
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
