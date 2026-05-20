from flask import Blueprint, g, jsonify

from app.core.security.auth_guard import require_auth
from app.models.usage import FeatureLimit
from app.services.usage.usage_service import UsageService


limits_bp = Blueprint("limits", __name__)


def _warning_level(percent: int, exhausted: bool) -> str | None:
    if exhausted or percent >= 100:
        return "100"
    if percent >= 90:
        return "90"
    if percent >= 75:
        return "75"
    return None


@limits_bp.get("/status")
@require_auth
def get_limits_status():
    usage_service = UsageService()
    limits = FeatureLimit.query.filter_by(plan_id=g.current_user.plan_id).order_by(FeatureLimit.feature_key.asc()).all() if g.current_user.plan_id else []

    features = []
    for limit in limits:
        status = usage_service.get_status(g.current_user.id, limit.feature_key, g.current_user.plan_id)
        percent = status.get("percent", 0)
        exhausted = bool(status.get("exhausted", False))
        features.append(
            {
                "feature_key": limit.feature_key,
                "used": status.get("used"),
                "quota": status.get("quota"),
                "remaining": status.get("remaining"),
                "percent": percent,
                "warning_level": _warning_level(percent, exhausted),
                "exhausted": exhausted,
            }
        )

    return jsonify({"plan_id": g.current_user.plan_id, "features": features}), 200
