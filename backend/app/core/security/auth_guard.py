from functools import wraps

from flask import g, request

from app.common.responses import error_response
from app.models.user import User
from app.core.security.token_service import decode_access_token


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return error_response("unauthorized", "Missing bearer token", 401)
        payload = decode_access_token(auth.replace("Bearer ", "", 1).strip())
        user = User.query.get(payload.get("sub"))
        if not user or not user.is_active:
            return error_response("unauthorized", "Invalid user", 401)
        g.current_user = user
        return fn(*args, **kwargs)
    return wrapper
