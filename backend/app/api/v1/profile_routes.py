from __future__ import annotations

from flask import Blueprint, g, request

from app.common.responses import error_response, ok
from app.core.security.auth_guard import require_auth
from app.services.user.user_experience_service import UserExperienceService

profile_bp = Blueprint("profile", __name__)
_service = UserExperienceService()


@profile_bp.get("/")
@require_auth
def get_profile_status():
    return ok(_service.profile_payload(g.current_user))


@profile_bp.patch("/")
@require_auth
def update_profile():
    payload = request.get_json(silent=True) or {}
    try:
        return ok(_service.update_profile(g.current_user, payload))
    except ValueError as exc:
        return error_response("validation_error", str(exc), 400)


@profile_bp.post("/onboarding")
@require_auth
def update_onboarding_profile():
    payload = request.get_json(silent=True) or {}
    allowed = {
        "display_name",
        "risk_profile",
        "preferred_horizon_days",
        "max_drawdown_tolerance",
        "capital",
        "preferred_currency",
        "locale",
        "timezone",
    }
    filtered = {key: value for key, value in payload.items() if key in allowed}
    try:
        profile = _service.update_profile(g.current_user, filtered)
        if any(key in payload for key in {"preferred_currency", "locale", "timezone"}):
            _service.update_settings(g.current_user, {key: payload[key] for key in ["preferred_currency", "locale", "timezone"] if key in payload})
        return ok({"profile": profile, "onboarding": _service.onboarding_status(g.current_user)})
    except ValueError as exc:
        return error_response("validation_error", str(exc), 400)
