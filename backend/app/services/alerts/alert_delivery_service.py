from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.extensions import db
from app.models.notification import Notification
from app.services.alerts.alert_rule_engine import AlertRuleEngine
from app.services.product.orca_product_suite import OrcaProductSuite


class AlertDeliveryService:
    """Turns evaluated alert events and product briefs into persisted user notifications.

    External delivery channels are represented honestly: in-app delivery is
    persisted now; email/telegram/push are marked as `not_configured` until a
    real provider is wired through configuration.
    """

    def __init__(self, engine: AlertRuleEngine | None = None, product_suite: OrcaProductSuite | None = None) -> None:
        self.engine = engine or AlertRuleEngine()
        self.product_suite = product_suite or OrcaProductSuite()

    def evaluate_and_deliver_for_user(self, user_id: str) -> dict:
        evaluation = self.engine.evaluate_for_user(user_id)
        return self._deliver_evaluation(evaluation)

    def evaluate_and_deliver_rule_for_user(self, rule_id: str, user_id: str) -> dict | None:
        evaluation = self.engine.evaluate_rule_for_user(rule_id=rule_id, user_id=user_id)
        if evaluation is None:
            return None
        return self._deliver_evaluation(evaluation)

    def evaluate_and_deliver_all(self) -> dict:
        evaluation = self.engine.evaluate_all()
        return self._deliver_evaluation(evaluation)

    def deliver_daily_brief_for_user(self, user_id: str, symbols: list[str] | None = None) -> dict:
        brief = self.product_suite.build_daily_brief(symbols=symbols)
        now = datetime.now(UTC)
        symbol_key = ",".join(symbols or ["default"])
        source_event_key = f"daily_brief:{user_id}:{now.date().isoformat()}:{symbol_key}"
        notification = self._get_or_create_notification(
            user_id=user_id,
            notification_type="daily_brief",
            source_event_key=source_event_key,
            title=brief["headline"],
            body=brief["summary"],
            data={"brief": brief, "delivery_status": self._delivery_status(["in_app", "email", "telegram"])},
        )
        db.session.commit()
        return {"created": notification["created"], "notification": self.serialize(notification["row"]), "brief": brief}

    def _deliver_evaluation(self, evaluation: dict) -> dict:
        delivered = []
        skipped = []
        for result in evaluation.get("triggered", []):
            event = result.get("last_event") or {}
            if not event.get("user_id"):
                skipped.append({"reason": "missing_user_id", "result": result})
                continue
            delivery = self._deliver_event(event)
            delivered.append(delivery)
        db.session.commit()
        return {
            **evaluation,
            "delivery_status": "in_app_persisted",
            "delivered_count": sum(1 for item in delivered if item["created"]),
            "duplicate_count": sum(1 for item in delivered if not item["created"]),
            "deliveries": delivered,
            "skipped_deliveries": skipped,
        }

    def _deliver_event(self, event: dict[str, Any]) -> dict:
        user_id = str(event["user_id"])
        rule_id = event.get("rule_id") or "unknown_rule"
        triggered_at = event.get("triggered_at") or datetime.now(UTC).isoformat()
        source_event_key = f"alert:{rule_id}:{triggered_at}"
        symbol = event.get("symbol") or "Asset"
        title = event.get("title") or f"{symbol} alarmı tetiklendi"
        body = self._event_body(event)
        delivery_status = self._delivery_status(event.get("channels") or ["in_app"])
        row_info = self._get_or_create_notification(
            user_id=user_id,
            notification_type="alert",
            source_event_key=source_event_key,
            title=title,
            body=body,
            data={"event": event, "delivery_status": delivery_status},
        )
        return {"created": row_info["created"], "notification": self.serialize(row_info["row"]), "delivery_status": delivery_status}

    @staticmethod
    def _event_body(event: dict[str, Any]) -> str:
        symbol = event.get("symbol") or "Asset"
        metric = event.get("metric") or "metric"
        condition = event.get("condition") or "condition"
        threshold = event.get("threshold")
        current_value = event.get("current_value")
        summary = event.get("asset_summary") or "Koşul gerçekleşti; karar vermeden önce risk/avantaj maddelerini kontrol et."
        return f"{symbol} için {metric} {condition} {threshold} koşulu tetiklendi. Güncel değer: {current_value}. {summary}"

    @staticmethod
    def _delivery_status(channels: list[str]) -> dict:
        status = {}
        for channel in channels:
            clean = str(channel).strip()
            if clean == "in_app":
                status[clean] = "created"
            elif clean:
                status[clean] = "not_configured"
        if "in_app" not in status:
            status["in_app"] = "created"
        return status

    @staticmethod
    def _get_or_create_notification(user_id: str, notification_type: str, source_event_key: str, title: str, body: str | None, data: dict) -> dict:
        existing = Notification.query.filter_by(source_event_key=source_event_key).one_or_none()
        if existing:
            return {"created": False, "row": existing}
        row = Notification(
            user_id=user_id,
            type=notification_type,
            status="unread",
            title=title[:255],
            body=body,
            source_event_key=source_event_key,
            data=data,
        )
        db.session.add(row)
        return {"created": True, "row": row}

    @staticmethod
    def serialize(notification: Notification) -> dict:
        return {
            "id": notification.id,
            "user_id": notification.user_id,
            "type": notification.type,
            "status": notification.status,
            "title": notification.title,
            "body": notification.body,
            "source_event_key": notification.source_event_key,
            "data": notification.data or {},
            "read_at": notification.read_at.isoformat() if notification.read_at else None,
            "created_at": notification.created_at.isoformat() if notification.created_at else None,
            "updated_at": notification.updated_at.isoformat() if notification.updated_at else None,
        }
