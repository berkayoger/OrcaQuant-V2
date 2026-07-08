from __future__ import annotations

from flask import Blueprint, g, request

from app.common.responses import error_response, ok
from app.core.security.auth_guard import require_auth
from app.services.user.user_experience_service import UserExperienceService

settings_bp = Blueprint("settings", __name__)
_service = UserExperienceService()


@settings_bp.get("/")
@require_auth
def get_settings_status():
    return ok(_service.settings_payload(g.current_user))


@settings_bp.patch("/")
@require_auth
def update_settings():
    payload = request.get_json(silent=True) or {}
    try:
        return ok(_service.update_settings(g.current_user, payload))
    except ValueError as exc:
        return error_response("validation_error", str(exc), 400)


@settings_bp.get("/notifications")
@require_auth
def get_notification_preferences():
    return ok(_service.settings_payload(g.current_user)["notification_preferences"])


@settings_bp.patch("/notifications")
@require_auth
def update_notification_preferences():
    payload = request.get_json(silent=True) or {}
    try:
        return ok(_service.update_notification_preferences(g.current_user, payload))
    except ValueError as exc:
        return error_response("validation_error", str(exc), 400)


@settings_bp.get("/privacy")
@require_auth
def get_privacy_preferences():
    return ok(_service.settings_payload(g.current_user)["privacy"])


@settings_bp.patch("/privacy")
@require_auth
def update_privacy_preferences():
    payload = request.get_json(silent=True) or {}
    try:
        return ok(_service.update_settings(g.current_user, {"privacy": payload})["privacy"])
    except ValueError as exc:
        return error_response("validation_error", str(exc), 400)
