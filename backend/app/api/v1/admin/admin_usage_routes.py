from flask import Blueprint, request

from app.common.responses import created, error_response, ok
from app.core.security.auth_guard import require_auth
from app.core.security.permission_guard import require_role
from app.extensions import db
from app.models.usage import DailyUsage
from app.models.user import User

admin_usage_bp = Blueprint("admin_usage", __name__)


def _serialize_usage(row: DailyUsage) -> dict:
    return {
        "id": row.id,
        "user_id": row.user_id,
        "feature_key": row.feature_key,
        "used_count": row.used_count,
        "usage_date": row.usage_date.isoformat() if row.usage_date else None,
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "updated_at": row.updated_at.isoformat() if row.updated_at else None,
    }


@admin_usage_bp.get("")
@require_auth
@require_role("admin")
def list_admin_usage():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=20, type=int)
    if not page or page < 1 or not per_page or per_page < 1 or per_page > 100:
        return error_response("validation_error", "page must be >= 1 and per_page must be 1..100", 400)
    query = DailyUsage.query
    user_id = request.args.get("user_id", type=str)
    if user_id:
        query = query.filter_by(user_id=user_id)
    pagination = query.order_by(DailyUsage.usage_date.desc(), DailyUsage.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return ok({"items": [_serialize_usage(i) for i in pagination.items], "pagination": {"page": page, "per_page": per_page, "total": pagination.total, "pages": pagination.pages}})


@admin_usage_bp.post("")
@require_auth
@require_role("admin")
def create_admin_usage():
    payload = request.get_json(silent=True) or {}
    user_id = payload.get("user_id")
    feature_key = (payload.get("feature_key") or "").strip()
    used_count = payload.get("used_count", 0)
    if not user_id or not feature_key:
        return error_response("validation_error", "user_id and feature_key are required", 400)
    if not isinstance(used_count, int) or used_count < 0:
        return error_response("validation_error", "used_count must be a non-negative integer", 400)
    if not User.query.filter_by(id=user_id).one_or_none():
        return error_response("validation_error", "user_id does not exist", 400)
    row = DailyUsage(user_id=user_id, feature_key=feature_key, used_count=used_count)
    db.session.add(row)
    db.session.commit()
    return created(_serialize_usage(row))
