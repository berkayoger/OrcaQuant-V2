from functools import wraps
from flask import g
from app.common.responses import error_response
from app.services.usage.usage_service import UsageService

def enforce_usage_limit(feature_key: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = getattr(g, "current_user", None)
            if not user:
                return error_response("forbidden", "Auth required", 403)
            status = UsageService().check_limit(user.id, feature_key)
            if status["exhausted"]:
                return error_response("quota_exceeded", "Usage limit reached", 429)
            return fn(*args, **kwargs)
        return wrapper
    return decorator
