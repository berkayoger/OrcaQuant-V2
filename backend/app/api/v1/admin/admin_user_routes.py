from flask import Blueprint, request

from app.common.responses import error_response, ok
from app.core.security.auth_guard import require_auth
from app.core.security.permission_guard import require_role
from app.extensions import db
from app.models.user import User


admin_user_bp = Blueprint("admin_users", __name__)


def _parse_pagination() -> tuple[int, int] | tuple[None, None]:
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=20, type=int)
    if not page or page < 1 or not per_page or per_page < 1 or per_page > 100:
        return None, None
    return page, per_page


def _serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "plan_id": getattr(user, "plan_id", None),
        "subscription_status": getattr(user, "subscription_status", None),
        "created_at": user.created_at.isoformat() if getattr(user, "created_at", None) else None,
        "updated_at": user.updated_at.isoformat() if getattr(user, "updated_at", None) else None,
    }


@admin_user_bp.get("")
@require_auth
@require_role("admin")
def list_admin_users():
    page, per_page = _parse_pagination()
    if page is None:
        return error_response("validation_error", "page must be >= 1 and per_page must be 1..100", 400)

    pagination = User.query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return ok(
        {
            "items": [_serialize_user(user) for user in pagination.items],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": pagination.total,
                "pages": pagination.pages,
            },
        }
    )


@admin_user_bp.patch("/<user_id>")
@require_auth
@require_role("admin")
def patch_admin_user(user_id: str):
    payload = request.get_json(silent=True) or {}
    allowed = {"role", "plan_id", "subscription_status"}
    unknown = set(payload.keys()) - allowed
    if unknown:
        return error_response("validation_error", f"Unknown fields: {', '.join(sorted(unknown))}", 400)
    user = User.query.filter_by(id=user_id).one_or_none()
    if not user:
        return error_response("not_found", "User not found", 404)
    if "role" in payload:
        if payload["role"] not in {"user", "admin"}:
            return error_response("validation_error", "role must be user or admin", 400)
        user.role = payload["role"]
    if "plan_id" in payload:
        user.plan_id = payload["plan_id"]
    if "subscription_status" in payload:
        user.subscription_status = payload["subscription_status"]
    db.session.commit()
    return ok(_serialize_user(user))
