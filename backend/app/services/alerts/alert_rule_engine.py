from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from app.extensions import db
from app.models.alert_rule import AlertRule
from app.services.dashboard.market_cockpit_service import MarketCockpitService


class AlertRuleEngine:
    """Evaluates saved alert rules against the current Market Cockpit snapshot.

    Alert rules are intentionally stored in the existing JSON `data` column so
    the first production-ready evaluation loop can be added without a migration.
    A notification worker can later consume `last_event` records or call this
    service on a schedule.
    """

    SUPPORTED_METRICS = {"price", "opportunity_score", "risk_score", "technical_score", "volume_score", "change_24h_pct"}
    SUPPORTED_CONDITIONS = {">=", "<=", "crosses_above", "crosses_below"}

    def __init__(self, cockpit_service: MarketCockpitService | None = None) -> None:
        self.cockpit_service = cockpit_service or MarketCockpitService()

    def evaluate_for_user(self, user_id: str) -> dict:
        rules = AlertRule.query.filter_by(user_id=user_id).order_by(AlertRule.created_at.asc()).all()
        return self.evaluate_rules(rules)

    def evaluate_rule_for_user(self, rule_id: str, user_id: str) -> dict | None:
        rule = AlertRule.query.filter_by(id=rule_id, user_id=user_id).one_or_none()
        if not rule:
            return None
        return self.evaluate_rules([rule])

    def evaluate_all(self) -> dict:
        rules = AlertRule.query.order_by(AlertRule.created_at.asc()).all()
        return self.evaluate_rules(rules)

    def evaluate_rules(self, rules: list[AlertRule]) -> dict:
        enabled_rules = [rule for rule in rules if (rule.data or {}).get("enabled", True)]
        symbols = self._symbols_for_rules(enabled_rules)
        cockpit = self.cockpit_service.build_cockpit(symbols=symbols) if symbols else None
        assets_by_symbol = {asset["symbol"]: asset for asset in cockpit["assets"]} if cockpit else {}

        results = []
        for rule in rules:
            result = self.evaluate_rule(rule, assets_by_symbol)
            results.append(result)

        db.session.commit()
        triggered = [item for item in results if item["triggered"]]
        suppressed = [item for item in results if item.get("suppressed")]
        return {
            "evaluated": len(results),
            "enabled": len(enabled_rules),
            "triggered_count": len(triggered),
            "suppressed_count": len(suppressed),
            "triggered": triggered,
            "results": results,
            "notification_status": "ready_for_delivery_worker",
        }

    def evaluate_rule(self, rule: AlertRule, assets_by_symbol: dict[str, dict]) -> dict:
        data = dict(rule.data or {})
        now = datetime.now(UTC)
        if not data.get("enabled", True):
            return self._result(rule, data, status="disabled", triggered=False, now=now)

        symbol = self._normalize_symbol(data.get("symbol") or "")
        metric = data.get("metric")
        condition = data.get("condition")
        threshold = data.get("threshold")
        asset = assets_by_symbol.get(symbol)

        if not asset:
            return self._save_result(rule, data, status="asset_not_found", triggered=False, now=now)
        if metric not in self.SUPPORTED_METRICS or condition not in self.SUPPORTED_CONDITIONS:
            return self._save_result(rule, data, status="invalid_rule", triggered=False, now=now)

        current_value = self._metric_value(asset, str(metric))
        previous_value = self._as_float(data.get("last_value"))
        threshold_value = self._as_float(threshold)
        if current_value is None or threshold_value is None:
            return self._save_result(rule, data, status="metric_unavailable", triggered=False, now=now)

        condition_met = self._condition_met(
            condition=str(condition),
            current_value=current_value,
            threshold=threshold_value,
            previous_value=previous_value,
        )
        cooldown_active = self._cooldown_active(data, now) if condition_met else False
        triggered = bool(condition_met and not cooldown_active)
        status = "triggered" if triggered else "suppressed_by_cooldown" if cooldown_active else "not_triggered"

        data["symbol"] = symbol
        data["last_value"] = current_value
        data["last_evaluated_at"] = now.isoformat()
        data["last_result"] = status
        if triggered:
            data["trigger_count"] = int(data.get("trigger_count") or 0) + 1
            data["last_triggered_at"] = now.isoformat()
            data["last_event"] = self._event(rule, data, asset, current_value, threshold_value, now)
        rule.data = data

        result = self._result(rule, data, status=status, triggered=triggered, now=now)
        result.update(
            {
                "current_value": current_value,
                "previous_value": previous_value,
                "threshold": threshold_value,
                "condition_met": condition_met,
                "suppressed": cooldown_active,
                "asset_label": asset.get("label"),
                "asset_summary": asset.get("plain_language_summary"),
            }
        )
        return result

    @classmethod
    def normalize_rule_payload(cls, payload: dict[str, Any], existing: dict[str, Any] | None = None) -> tuple[dict[str, Any] | None, str | None]:
        merged = {**(existing or {}), **payload}
        symbol = cls._normalize_symbol(merged.get("symbol") or "")
        metric = str(merged.get("metric") or "").strip()
        condition = str(merged.get("condition") or "").strip()
        threshold = cls._as_float(merged.get("threshold"))
        title = str(merged.get("title") or "").strip() or None
        enabled = merged.get("enabled", True)
        cooldown_minutes = merged.get("cooldown_minutes", 60)
        channels = merged.get("channels") or ["in_app"]

        if not symbol:
            return None, "symbol is required"
        if metric not in cls.SUPPORTED_METRICS:
            return None, f"metric must be one of {sorted(cls.SUPPORTED_METRICS)}"
        if condition not in cls.SUPPORTED_CONDITIONS:
            return None, f"condition must be one of {sorted(cls.SUPPORTED_CONDITIONS)}"
        if threshold is None:
            return None, "threshold must be numeric"
        if not isinstance(enabled, bool):
            return None, "enabled must be boolean"
        try:
            cooldown_minutes = max(0, int(cooldown_minutes))
        except (TypeError, ValueError):
            return None, "cooldown_minutes must be an integer"
        if not isinstance(channels, list) or not all(isinstance(channel, str) and channel.strip() for channel in channels):
            return None, "channels must be a list of strings"

        normalized = {
            **merged,
            "symbol": symbol,
            "metric": metric,
            "condition": condition,
            "threshold": threshold,
            "title": title or f"{symbol} {metric} {condition} {threshold}",
            "enabled": enabled,
            "cooldown_minutes": cooldown_minutes,
            "channels": [channel.strip() for channel in channels],
        }
        return normalized, None

    @staticmethod
    def _symbols_for_rules(rules: list[AlertRule]) -> list[str]:
        seen: set[str] = set()
        symbols: list[str] = []
        for rule in rules:
            symbol = AlertRuleEngine._normalize_symbol((rule.data or {}).get("symbol") or "")
            if symbol and symbol not in seen:
                seen.add(symbol)
                symbols.append(symbol)
        return symbols

    @staticmethod
    def _normalize_symbol(symbol: str) -> str:
        return "".join(ch for ch in str(symbol).upper().strip() if ch.isalnum())

    @staticmethod
    def _as_float(value: Any) -> float | None:
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _metric_value(asset: dict, metric: str) -> float | None:
        value = asset.get(metric)
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _condition_met(condition: str, current_value: float, threshold: float, previous_value: float | None) -> bool:
        if condition == ">=":
            return current_value >= threshold
        if condition == "<=":
            return current_value <= threshold
        if condition == "crosses_above":
            return previous_value is not None and previous_value < threshold <= current_value
        if condition == "crosses_below":
            return previous_value is not None and previous_value > threshold >= current_value
        return False

    @staticmethod
    def _cooldown_active(data: dict, now: datetime) -> bool:
        cooldown_minutes = int(data.get("cooldown_minutes") or 0)
        last_triggered_at = AlertRuleEngine._parse_datetime(data.get("last_triggered_at"))
        if cooldown_minutes <= 0 or not last_triggered_at:
            return False
        return now - last_triggered_at < timedelta(minutes=cooldown_minutes)

    @staticmethod
    def _parse_datetime(value: Any) -> datetime | None:
        if not value:
            return None
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)

    @staticmethod
    def _event(rule: AlertRule, data: dict, asset: dict, current_value: float, threshold: float, now: datetime) -> dict:
        return {
            "rule_id": rule.id,
            "user_id": rule.user_id,
            "symbol": data.get("symbol"),
            "metric": data.get("metric"),
            "condition": data.get("condition"),
            "threshold": threshold,
            "current_value": current_value,
            "title": data.get("title"),
            "asset_label": asset.get("label"),
            "asset_summary": asset.get("plain_language_summary"),
            "triggered_at": now.isoformat(),
            "delivery_status": "pending_delivery_worker",
            "channels": data.get("channels") or ["in_app"],
        }

    @staticmethod
    def _result(rule: AlertRule, data: dict, status: str, triggered: bool, now: datetime) -> dict:
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
            "status": status,
            "triggered": triggered,
            "trigger_count": int(data.get("trigger_count") or 0),
            "last_value": data.get("last_value"),
            "last_evaluated_at": data.get("last_evaluated_at") or now.isoformat(),
            "last_triggered_at": data.get("last_triggered_at"),
            "last_event": data.get("last_event"),
        }

    @staticmethod
    def _save_result(rule: AlertRule, data: dict, status: str, triggered: bool, now: datetime) -> dict:
        data["last_evaluated_at"] = now.isoformat()
        data["last_result"] = status
        rule.data = data
        return AlertRuleEngine._result(rule, data, status=status, triggered=triggered, now=now)
