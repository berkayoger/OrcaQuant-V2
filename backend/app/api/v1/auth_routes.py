from flask import Blueprint, jsonify, request

from app.repositories.user_repository import UserRepository
from app.services.auth.login_service import LoginService
from app.services.auth.register_service import RegisterService


auth_bp = Blueprint("auth", __name__)
_user_repo = UserRepository()
_register_service = RegisterService(user_repository=_user_repo)
_login_service = LoginService(user_repository=_user_repo)


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
    return jsonify(_login_service.execute(payload)), 200
