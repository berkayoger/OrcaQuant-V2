from flask import Blueprint, jsonify, request

from app.core.security.token_service import create_refresh_token, decode_refresh_token
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
_refresh_service = RefreshService()
_logout_service = LogoutService()
_session_service = SessionService()


@auth_bp.get("/status")
def get_auth_status():
    return jsonify({"module": "auth", "status": "ok"}), 200


@auth_bp.post("/register")
def register():
    payload = request.get_json(silent=True) or {}
    return jsonify(_register_service.execute(payload)), 201


@auth_bp.post("/login")
def login():
    payload = request.get_json(silent=True) or {}
    result = _login_service.execute(payload)
    user_id = result.get("user", {}).get("id")
    if user_id:
        refresh_token, jti = create_refresh_token(user_id)
        _session_service.create_refresh_session(user_id=user_id, refresh_token=refresh_token, jti=jti)
        result["refresh_token"] = refresh_token
    return jsonify(result), 200


@auth_bp.post("/refresh")
def refresh():
    payload = request.get_json(silent=True) or {}
    token = payload.get("refresh_token")
    if not token:
        return jsonify({"status": "error", "code": "missing_refresh_token"}), 400
    return jsonify(_refresh_service.execute(token)), 200


@auth_bp.post("/logout")
def logout():
    payload = request.get_json(silent=True) or {}
    token = payload.get("refresh_token")
    if not token:
        return jsonify({"status": "error", "code": "missing_refresh_token"}), 400
    jti = decode_refresh_token(token).get("jti")
    if not jti or not _logout_service.execute(jti):
        return jsonify({"status": "error", "code": "session_not_found"}), 400
    return jsonify({"status": "ok"}), 200
