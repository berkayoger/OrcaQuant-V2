from flask import Blueprint, request

from app.common.responses import created, error_response, ok
from app.core.security.auth_guard import require_auth
from app.core.security.permission_guard import require_role
from app.extensions import db
from app.models.plan import Plan

admin_plan_bp = Blueprint("admin_plans", __name__)


def _serialize_plan(plan: Plan) -> dict:
    return {
        "id": plan.id,
        "code": plan.code,
        "name": plan.name,
        "description": plan.description,
        "is_active": plan.is_active,
        "sort_order": plan.sort_order,
        "created_at": plan.created_at.isoformat() if plan.created_at else None,
        "updated_at": plan.updated_at.isoformat() if plan.updated_at else None,
    }


def _parse_pagination() -> tuple[int, int] | tuple[None, None]:
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=20, type=int)
    if not page or page < 1 or not per_page or per_page < 1 or per_page > 100:
        return None, None
    return page, per_page


@admin_plan_bp.get("")
@require_auth
@require_role("admin")
def list_admin_plans():
    page, per_page = _parse_pagination()
    if page is None:
        return error_response("validation_error", "page must be >= 1 and per_page must be 1..100", 400)

    pagination = Plan.query.order_by(Plan.sort_order.asc(), Plan.created_at.asc()).paginate(page=page, per_page=per_page, error_out=False)
    return ok(
        {
            "items": [_serialize_plan(plan) for plan in pagination.items],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": pagination.total,
                "pages": pagination.pages,
            },
        }
    )


@admin_plan_bp.post("")
@require_auth
@require_role("admin")
def create_admin_plan():
    payload = request.get_json(silent=True) or {}
    code = (payload.get("code") or "").strip().lower()
    name = (payload.get("name") or "").strip()
    description = payload.get("description")
    if description is not None and not isinstance(description, str):
        return error_response("validation_error", "description must be a string", 400)

    is_active = payload.get("is_active", True)
    sort_order = payload.get("sort_order", 0)

    if not code or not name:
        return error_response("validation_error", "code and name are required", 400)
    if not isinstance(is_active, bool):
        return error_response("validation_error", "is_active must be a boolean", 400)
    if not isinstance(sort_order, int):
        return error_response("validation_error", "sort_order must be an integer", 400)
    if Plan.query.filter_by(code=code).one_or_none():
        return error_response("duplicate_resource", "plan code already exists", 409)

    plan = Plan(code=code, name=name, description=description, is_active=is_active, sort_order=sort_order)
    db.session.add(plan)
    db.session.commit()
    return created(_serialize_plan(plan))


@admin_plan_bp.patch("/<plan_id>")
@require_auth
@require_role("admin")
def patch_admin_plan(plan_id: str):
    payload = request.get_json(silent=True) or {}
    allowed = {"code", "name", "description", "is_active", "sort_order"}
    unknown = set(payload.keys()) - allowed
    if unknown:
        return error_response("validation_error", f"Unknown fields: {', '.join(sorted(unknown))}", 400)

    plan = Plan.query.filter_by(id=plan_id).one_or_none()
    if not plan:
        return error_response("not_found", "Plan not found", 404)

    if "code" in payload:
        code = (payload.get("code") or "").strip().lower()
        if not code:
            return error_response("validation_error", "code cannot be empty", 400)
        existing = Plan.query.filter(Plan.code == code, Plan.id != plan.id).one_or_none()
        if existing:
            return error_response("duplicate_resource", "plan code already exists", 409)
        plan.code = code
    if "name" in payload:
        name = (payload.get("name") or "").strip()
        if not name:
            return error_response("validation_error", "name cannot be empty", 400)
        plan.name = name
    if "description" in payload:
        if payload["description"] is not None and not isinstance(payload["description"], str):
            return error_response("validation_error", "description must be a string", 400)
        plan.description = payload["description"]
    if "is_active" in payload:
        if not isinstance(payload["is_active"], bool):
            return error_response("validation_error", "is_active must be a boolean", 400)
        plan.is_active = payload["is_active"]
    if "sort_order" in payload:
        if not isinstance(payload["sort_order"], int):
            return error_response("validation_error", "sort_order must be an integer", 400)
        plan.sort_order = payload["sort_order"]

    db.session.commit()
    return ok(_serialize_plan(plan))
