from flask import Blueprint, request

from app.common.responses import created, error_response, ok
from app.core.security.auth_guard import require_auth
from app.core.security.permission_guard import require_role
from app.extensions import db
from app.models.plan import Plan
from app.models.usage import FeatureLimit

admin_limit_bp = Blueprint("admin_limits", __name__)


def _serialize_limit(limit: FeatureLimit) -> dict:
    return {
        "id": limit.id,
        "plan_id": limit.plan_id,
        "feature_key": limit.feature_key,
        "daily_quota": limit.daily_quota,
        "monthly_quota": limit.monthly_quota,
        "enabled": limit.enabled,
        "created_at": limit.created_at.isoformat() if limit.created_at else None,
        "updated_at": limit.updated_at.isoformat() if limit.updated_at else None,
    }


@admin_limit_bp.get("")
@require_auth
@require_role("admin")
def list_admin_limits():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=20, type=int)
    plan_id = request.args.get("plan_id", type=str)
    if not page or page < 1 or not per_page or per_page < 1 or per_page > 100:
        return error_response("validation_error", "page must be >= 1 and per_page must be 1..100", 400)

    query = FeatureLimit.query
    if plan_id:
        query = query.filter_by(plan_id=plan_id)
    pagination = query.order_by(FeatureLimit.feature_key.asc(), FeatureLimit.created_at.asc()).paginate(page=page, per_page=per_page, error_out=False)
    return ok({
        "items": [_serialize_limit(limit) for limit in pagination.items],
        "pagination": {"page": page, "per_page": per_page, "total": pagination.total, "pages": pagination.pages},
    })


@admin_limit_bp.post("")
@require_auth
@require_role("admin")
def create_admin_limit():
    payload = request.get_json(silent=True) or {}
    plan_id = payload.get("plan_id")
    feature_key = (payload.get("feature_key") or "").strip()
    daily_quota = payload.get("daily_quota")
    monthly_quota = payload.get("monthly_quota")
    enabled = payload.get("enabled", True)

    if not plan_id or not feature_key:
        return error_response("validation_error", "plan_id and feature_key are required", 400)
    if not Plan.query.filter_by(id=plan_id).one_or_none():
        return error_response("validation_error", "plan_id does not exist", 400)
    if daily_quota is not None and (not isinstance(daily_quota, int) or daily_quota < 0):
        return error_response("validation_error", "daily_quota must be a non-negative integer or null", 400)
    if monthly_quota is not None and (not isinstance(monthly_quota, int) or monthly_quota < 0):
        return error_response("validation_error", "monthly_quota must be a non-negative integer or null", 400)
    if not isinstance(enabled, bool):
        return error_response("validation_error", "enabled must be a boolean", 400)
    if FeatureLimit.query.filter_by(plan_id=plan_id, feature_key=feature_key).one_or_none():
        return error_response("duplicate_resource", "feature limit already exists for this plan/feature", 409)

    limit = FeatureLimit(plan_id=plan_id, feature_key=feature_key, daily_quota=daily_quota, monthly_quota=monthly_quota, enabled=enabled)
    db.session.add(limit)
    db.session.commit()
    return created(_serialize_limit(limit))


@admin_limit_bp.patch("/<limit_id>")
@require_auth
@require_role("admin")
def patch_admin_limit(limit_id: str):
    payload = request.get_json(silent=True) or {}
    allowed = {"feature_key", "daily_quota", "monthly_quota", "enabled"}
    unknown = set(payload.keys()) - allowed
    if unknown:
        return error_response("validation_error", f"Unknown fields: {', '.join(sorted(unknown))}", 400)

    limit = FeatureLimit.query.filter_by(id=limit_id).one_or_none()
    if not limit:
        return error_response("not_found", "Limit not found", 404)

    if "feature_key" in payload:
        feature_key = (payload["feature_key"] or "").strip()
        if not feature_key:
            return error_response("validation_error", "feature_key cannot be empty", 400)
        existing = FeatureLimit.query.filter(
            FeatureLimit.plan_id == limit.plan_id,
            FeatureLimit.feature_key == feature_key,
            FeatureLimit.id != limit.id,
        ).one_or_none()
        if existing:
            return error_response("duplicate_resource", "feature limit already exists for this plan/feature", 409)
        limit.feature_key = feature_key
    if "daily_quota" in payload:
        daily = payload["daily_quota"]
        if daily is not None and (not isinstance(daily, int) or daily < 0):
            return error_response("validation_error", "daily_quota must be a non-negative integer or null", 400)
        limit.daily_quota = daily
    if "monthly_quota" in payload:
        monthly = payload["monthly_quota"]
        if monthly is not None and (not isinstance(monthly, int) or monthly < 0):
            return error_response("validation_error", "monthly_quota must be a non-negative integer or null", 400)
        limit.monthly_quota = monthly
    if "enabled" in payload:
        if not isinstance(payload["enabled"], bool):
            return error_response("validation_error", "enabled must be a boolean", 400)
        limit.enabled = payload["enabled"]

    db.session.commit()
    return ok(_serialize_limit(limit))
