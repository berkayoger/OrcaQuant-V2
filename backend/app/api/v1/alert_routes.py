from __future__ import annotations

from flask import Blueprint, g, request

from app.common.responses import created, error_response, ok
from app.core.security.auth_guard import require_auth
from app.extensions import db
from app.models.alert_rule import AlertRule
from app.services.alerts.alert_delivery_service import AlertDeliveryService
from app.services.alerts.alert_rule_engine import AlertRuleEngine
from app.services.dashboard.market_cockpit_service import MarketCockpitService

alert_bp = Blueprint("alerts", __name__)


def _serialize(rule: AlertRule) -> dict:
    data = rule.data or {}
    return {
        "id": rule.id,
        "user_id": rule.user_id,
        "symbol": data.get("symbol"),
        "metric": data.get("metric"),
        "condition": data.get("condition"),
        "threshold": data.get("threshold"),
        "title": data.get("title"),
        "enabled": data.get("enabled", True),
        "cooldown_minutes": data.get("cooldown_minutes", 60),
        "channels": data.get("channels") or ["in_app"],
        "last_value": data.get("last_value"),
        "last_result": data.get("last_result"),
        "last_evaluated_at": data.get("last_evaluated_at"),
        "last_triggered_at": data.get("last_triggered_at"),
        "trigger_count": data.get("trigger_count", 0),
        "last_event": data.get("last_event"),
        "created_at": rule.created_at.isoformat() if rule.created_at else None,
        "updated_at": rule.updated_at.isoformat() if rule.updated_at else None,
    }


def _normalize_payload(payload: dict, existing: dict | None = None) -> tuple[dict | None, tuple | None]:
    data, error = AlertRuleEngine.normalize_rule_payload(payload, existing=existing)
    if error:
        return None, error_response("validation_error", error, 400)
    return data, None


@alert_bp.get("/")
@require_auth
def list_alert_rules():
    rows = AlertRule.query.filter_by(user_id=g.current_user.id).order_by(AlertRule.created_at.desc()).all()
    return ok({"items": [_serialize(row) for row in rows]})


@alert_bp.post("/")
@require_auth
def create_alert_rule():
    payload = request.get_json(silent=True) or {}
    data, error = _normalize_payload(payload)
    if error:
        return error
    row = AlertRule(user_id=g.current_user.id, data=data)
    db.session.add(row)
    db.session.commit()
    return created(_serialize(row))


@alert_bp.post("/evaluate")
@require_auth
def evaluate_current_user_alerts():
    result = AlertDeliveryService().evaluate_and_deliver_for_user(g.current_user.id)
    return ok(result)


@alert_bp.patch("/<rule_id>")
@require_auth
def update_alert_rule(rule_id: str):
    row = AlertRule.query.filter_by(id=rule_id, user_id=g.current_user.id).one_or_none()
    if not row:
        return error_response("not_found", "Alert rule not found", 404)
    payload = request.get_json(silent=True) or {}
    data, error = _normalize_payload(payload, existing=row.data or {})
    if error:
        return error
    row.data = data
    db.session.commit()
    return ok(_serialize(row))


@alert_bp.post("/<rule_id>/evaluate")
@require_auth
def evaluate_single_alert_rule(rule_id: str):
    result = AlertDeliveryService().evaluate_and_deliver_rule_for_user(rule_id=rule_id, user_id=g.current_user.id)
    if result is None:
        return error_response("not_found", "Alert rule not found", 404)
    return ok(result)


@alert_bp.delete("/<rule_id>")
@require_auth
def delete_alert_rule(rule_id: str):
    row = AlertRule.query.filter_by(id=rule_id, user_id=g.current_user.id).one_or_none()
    if not row:
        return error_response("not_found", "Alert rule not found", 404)
    db.session.delete(row)
    db.session.commit()
    return ok({"deleted": True, "id": rule_id})


@alert_bp.get("/suggestions")
def get_alert_suggestions():
    symbols = [part.strip() for part in request.args.get("symbols", "").split(",") if part.strip()]
    radar = MarketCockpitService().build_radar(symbols=symbols or None)
    return ok({"items": radar["suggested_alerts"], "source": radar["status"]})
