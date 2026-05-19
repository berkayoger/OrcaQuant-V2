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
            status = service.check_limit(user.id, feature_key, getattr(user, "plan_id", None))
            if status["quota"] == 0 and feature_key in PROTECTED_FEATURES:
                return error_response("feature_disabled", "Feature quota is not configured", 403)
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
