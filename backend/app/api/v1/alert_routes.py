from __future__ import annotations

from flask import Blueprint, g, request

from app.common.responses import created, error_response, ok
from app.core.security.auth_guard import require_auth
from app.extensions import db
from app.models.alert_rule import AlertRule
from app.services.dashboard.market_cockpit_service import MarketCockpitService

alert_bp = Blueprint("alerts", __name__)

_ALLOWED_METRICS = {"price", "opportunity_score", "risk_score", "technical_score", "volume_score"}
_ALLOWED_CONDITIONS = {">=", "<=", "crosses_above", "crosses_below"}


def _normalize_symbol(symbol: str) -> str:
    return "".join(ch for ch in str(symbol).upper().strip() if ch.isalnum())


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
        "created_at": rule.created_at.isoformat() if rule.created_at else None,
        "updated_at": rule.updated_at.isoformat() if rule.updated_at else None,
    }


def _validated_payload(payload: dict) -> tuple[dict | None, tuple | None]:
    symbol = _normalize_symbol(payload.get("symbol") or "")
    metric = str(payload.get("metric") or "").strip()
    condition = str(payload.get("condition") or "").strip()
    threshold = payload.get("threshold")
    title = str(payload.get("title") or "").strip() or None
    enabled = payload.get("enabled", True)

    if not symbol:
        return None, error_response("validation_error", "symbol is required", 400)
    if metric not in _ALLOWED_METRICS:
        return None, error_response("validation_error", f"metric must be one of {sorted(_ALLOWED_METRICS)}", 400)
    if condition not in _ALLOWED_CONDITIONS:
        return None, error_response("validation_error", f"condition must be one of {sorted(_ALLOWED_CONDITIONS)}", 400)
    try:
        threshold = float(threshold)
    except (TypeError, ValueError):
        return None, error_response("validation_error", "threshold must be numeric", 400)
    if not isinstance(enabled, bool):
        return None, error_response("validation_error", "enabled must be boolean", 400)

    return {
        "symbol": symbol,
        "metric": metric,
        "condition": condition,
        "threshold": threshold,
        "title": title or f"{symbol} {metric} {condition} {threshold}",
        "enabled": enabled,
    }, None


@alert_bp.get("/")
@require_auth
def list_alert_rules():
    rows = AlertRule.query.filter_by(user_id=g.current_user.id).order_by(AlertRule.created_at.desc()).all()
    return ok({"items": [_serialize(row) for row in rows]})


@alert_bp.post("/")
@require_auth
def create_alert_rule():
    payload = request.get_json(silent=True) or {}
    data, error = _validated_payload(payload)
    if error:
        return error
    row = AlertRule(user_id=g.current_user.id, data=data)
    db.session.add(row)
    db.session.commit()
    return created(_serialize(row))


@alert_bp.patch("/<rule_id>")
@require_auth
def update_alert_rule(rule_id: str):
    row = AlertRule.query.filter_by(id=rule_id, user_id=g.current_user.id).one_or_none()
    if not row:
        return error_response("not_found", "Alert rule not found", 404)
    payload = {**(row.data or {}), **(request.get_json(silent=True) or {})}
    data, error = _validated_payload(payload)
    if error:
        return error
    row.data = data
    db.session.commit()
    return ok(_serialize(row))


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
