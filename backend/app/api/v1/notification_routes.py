from __future__ import annotations

from flask import Blueprint, g, request

from app.common.responses import error_response, ok
from app.core.security.auth_guard import require_auth
from app.extensions import db
from app.models.notification import Notification
from app.services.alerts.alert_delivery_service import AlertDeliveryService

notification_bp = Blueprint("notifications", __name__)


def _serialize(row: Notification) -> dict:
    return AlertDeliveryService.serialize(row)


@notification_bp.get("/")
@require_auth
def list_notifications():
    status = request.args.get("status", "all")
    query = Notification.query.filter_by(user_id=g.current_user.id)
    if status in {"read", "unread"}:
        query = query.filter_by(status=status)
    rows = query.order_by(Notification.created_at.desc()).limit(100).all()
    unread_count = Notification.query.filter_by(user_id=g.current_user.id, status="unread").count()
    return ok({"items": [_serialize(row) for row in rows], "unread_count": unread_count})


@notification_bp.post("/daily-brief")
@require_auth
def create_daily_brief_notification():
    payload = request.get_json(silent=True) or {}
    raw_symbols = payload.get("symbols") if isinstance(payload.get("symbols"), list) else []
    symbols = [str(symbol).strip() for symbol in raw_symbols if str(symbol).strip()]
    result = AlertDeliveryService().deliver_daily_brief_for_user(g.current_user.id, symbols=symbols or None)
    return ok(result)


@notification_bp.patch("/<notification_id>/read")
@require_auth
def mark_notification_read(notification_id: str):
    row = Notification.query.filter_by(id=notification_id, user_id=g.current_user.id).one_or_none()
    if not row:
        return error_response("not_found", "Notification not found", 404)
    row.mark_read()
    db.session.commit()
    return ok(_serialize(row))


@notification_bp.patch("/read-all")
@require_auth
def mark_all_notifications_read():
    rows = Notification.query.filter_by(user_id=g.current_user.id, status="unread").all()
    for row in rows:
        row.mark_read()
    db.session.commit()
    return ok({"updated": len(rows)})


@notification_bp.delete("/<notification_id>")
@require_auth
def delete_notification(notification_id: str):
    row = Notification.query.filter_by(id=notification_id, user_id=g.current_user.id).one_or_none()
    if not row:
        return error_response("not_found", "Notification not found", 404)
    db.session.delete(row)
    db.session.commit()
    return ok({"deleted": True, "id": notification_id})
