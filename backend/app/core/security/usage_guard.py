from functools import wraps

from flask import g, make_response

from app.common.responses import error_response
from app.services.usage.usage_service import UsageService


PROTECTED_FEATURES = {"technical_analysis", "scenario_risk", "full_analysis", "forecast", "decision_consensus", "llm_analyze", "realtime_stream"}


def enforce_usage_limit(feature_key: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = getattr(g, "current_user", None)
            if not user:
                return error_response("unauthorized", "Auth required", 401)

            service = UsageService()
            plan_id = getattr(user, "plan_id", None)
            if feature_key in PROTECTED_FEATURES and not plan_id:
                return error_response("plan_required", "An active plan is required", 403)

            status = service.check_limit(user.id, feature_key, plan_id)
            if feature_key in PROTECTED_FEATURES and not status.get("limit_exists"):
                return error_response("feature_not_configured", "Feature limit is not configured for this plan", 403)
            if feature_key in PROTECTED_FEATURES and not status.get("feature_enabled"):
                return error_response("feature_disabled", "Feature is disabled for this plan", 403)
            if status["exhausted"]:
                return error_response("quota_exceeded", "Usage limit reached", 429)

            response = make_response(fn(*args, **kwargs))
            if response.status_code < 400:
                updated = service.increment(user.id, feature_key, getattr(user, "plan_id", None))
                response.headers["X-Usage-Used"] = str(updated["used"])
                response.headers["X-Usage-Quota"] = str(updated["quota"])
                response.headers["X-Usage-Remaining"] = str(updated["remaining"])
            return response

        return wrapper

    return decorator
