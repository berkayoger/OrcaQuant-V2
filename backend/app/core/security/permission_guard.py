from functools import wraps
from flask import g
from app.common.responses import error_response

def require_role(role: str):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = getattr(g, "current_user", None)
            if not user or user.role != role:
                return error_response("forbidden", "Insufficient role", 403)
            return fn(*args, **kwargs)
        return wrapper
    return decorator
