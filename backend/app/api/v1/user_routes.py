from __future__ import annotations

from flask import Blueprint, g, jsonify, request

from app.common.responses import error_response, ok
from app.core.security.auth_guard import require_auth
from app.core.security.password_hasher import hash_password, verify_password
from app.extensions import db
from app.models.plan import Plan
from app.repositories.session_repository import SessionRepository
from app.services.account.username_service import UsernameService
from app.services.auth.session_service import SessionService
from app.services.usage.usage_service import UsageService
from app.services.user.user_experience_service import UserExperienceService


user_bp = Blueprint("user", __name__)
_username_service = UsernameService()
_user_experience = UserExperienceService()
_session_repository = SessionRepository()
_session_service = SessionService(repository=_session_repository)


@user_bp.get("/")
@require_auth
def get_user_status():
    plan = Plan.query.filter_by(id=g.current_user.plan_id).one_or_none() if g.current_user.plan_id else None
    return jsonify({
        "id": g.current_user.id,
        "email": g.current_user.email,
        "username": g.current_user.username,
        "role": g.current_user.role,
        "is_email_verified": g.current_user.is_email_verified,
        "plan_code": plan.code if plan else None,
        "subscription_status": g.current_user.subscription_status,
    }), 200


@user_bp.get("/home")
@require_auth
def get_user_home():
    return ok(_user_experience.home_payload(g.current_user))


@user_bp.get("/export")
@require_auth
def export_account_data():
    return ok(_user_experience.export_payload(g.current_user))


@user_bp.get("/sessions")
@require_auth
def list_sessions():
    return ok({"items": _user_experience.list_sessions(g.current_user.id)})


@user_bp.delete("/sessions/<session_id>")
@require_auth
def revoke_session(session_id: str):
    revoked = _session_repository.revoke_by_id_for_user(session_id=session_id, user_id=g.current_user.id)
    if not revoked:
        return error_response("not_found", "Session not found", 404)
    return ok({"revoked": True, "id": session_id})


@user_bp.delete("/sessions")
@require_auth
def revoke_all_sessions():
    revoked = _session_service.revoke_all_user_sessions(g.current_user.id)
    g.current_user.token_version = int(g.current_user.token_version or 0) + 1
    db.session.commit()
    return ok({"revoked": revoked})


@user_bp.patch("/password")
@require_auth
def change_password():
    payload = request.get_json(silent=True) or {}
    current_password = str(payload.get("current_password") or "")
    new_password = str(payload.get("new_password") or "")
    if len(new_password) < 8:
        return error_response("validation_error", "new_password must be at least 8 characters", 400)
    if not verify_password(current_password, g.current_user.password_hash):
        return error_response("authentication_error", "Current password is invalid", 401)
    g.current_user.password_hash = hash_password(new_password)
    g.current_user.token_version = int(g.current_user.token_version or 0) + 1
    _session_service.revoke_all_user_sessions(g.current_user.id)
    db.session.commit()
    return ok({"changed": True})


@user_bp.post("/deactivate")
@require_auth
def deactivate_account():
    payload = request.get_json(silent=True) or {}
    password = str(payload.get("password") or "")
    if not verify_password(password, g.current_user.password_hash):
        return error_response("authentication_error", "Password is invalid", 401)
    g.current_user.is_active = False
    g.current_user.token_version = int(g.current_user.token_version or 0) + 1
    revoked = _session_service.revoke_all_user_sessions(g.current_user.id)
    db.session.commit()
    return ok({"deactivated": True, "revoked_sessions": revoked})


@user_bp.get("/username/check")
@require_auth
def check_my_username_availability():
    username = request.args.get("username", "")
    return jsonify(_username_service.availability(username, current_user_id=g.current_user.id)), 200


@user_bp.patch("/username")
@require_auth
def change_username():
    payload = request.get_json(silent=True) or {}
    result = _username_service.claim_for_user(g.current_user, str(payload.get("username") or ""), reason="change")
    return jsonify(result), 200


@user_bp.get("/usage")
@require_auth
def get_usage_status():
    feature_key = request.args.get("feature_key", "technical_analysis")
    return jsonify(UsageService().get_status(g.current_user.id, feature_key, g.current_user.plan_id)), 200
