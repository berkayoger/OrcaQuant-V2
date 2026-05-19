from functools import wraps
from flask import g
from app.common.responses import error_response

def require_plan(_min_plan_code_or_feature: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if not getattr(g, "current_user", None):
                return error_response("forbidden", "Auth required", 403)
            # TODO(v1-migration): enforce plan hierarchy.
            return fn(*args, **kwargs)
        return wrapper
    return decorator
