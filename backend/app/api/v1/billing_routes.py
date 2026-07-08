from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from typing import Any

from flask import Blueprint, current_app, g, jsonify, request

from app.core.security.auth_guard import require_auth
from app.extensions import db
from app.models.payment import PaymentTransaction
from app.models.payment_event import PaymentEvent
from app.models.plan import Plan
from app.models.user import User
from app.payments.provider_base import ProviderInitiateRequest
from app.payments.provider_factory import get_payment_provider, get_provider_readiness, list_provider_readiness, supported_payment_providers

billing_bp = Blueprint("billing", __name__)


def _billing_enabled() -> bool:
    return bool(current_app.config.get("ENABLE_BILLING", False))


def _active_provider_name() -> str:
    return str(current_app.config.get("BILLING_PROVIDER", "fake")).strip().lower()


def _json_error(code: str, message: str, status_code: int):
    return jsonify({"code": code, "message": message}), status_code


@billing_bp.get("/status")
def get_billing_status():
    enabled = _billing_enabled()
    active_provider = _active_provider_name()
    try:
        active_readiness = get_provider_readiness(active_provider).to_dict()
        provider_error = None
    except ValueError as exc:
        active_readiness = None
        provider_error = str(exc)

    return jsonify(
        {
            "module": "billing",
            "enabled": enabled,
            "status": "ready_for_external_binding" if enabled else "disabled",
            "active_provider": active_provider,
            "active_provider_readiness": active_readiness,
            "provider_error": provider_error,
            "supported_providers": supported_payment_providers(),
            "providers": list_provider_readiness(),
        }
    ), 200


@billing_bp.get("/providers")
def list_billing_providers():
    return jsonify({"module": "billing_providers", "providers": list_provider_readiness()}), 200


@billing_bp.post("/initiate")
@require_auth
def initiate_billing():
    if not _billing_enabled():
        return _json_error("billing_disabled", "Billing is disabled", 501)

    idem_key = request.headers.get("Idempotency-Key", "").strip()
    if not idem_key:
        return _json_error("missing_idempotency_key", "Idempotency-Key header is required", 400)

    payload = request.get_json(silent=True) or {}
    plan_code = str(payload.get("plan_code") or "").strip()
    amount_raw = payload.get("amount")
    currency = str(payload.get("currency") or "TRY").strip().upper()
    if not plan_code:
        return _json_error("invalid_plan_code", "plan_code is required", 400)
    try:
        amount = Decimal(str(amount_raw))
    except (InvalidOperation, TypeError):
        return _json_error("invalid_amount", "amount must be numeric", 400)
    if amount <= 0:
        return _json_error("invalid_amount", "amount must be greater than zero", 400)
    allowed_currencies = {str(item).upper() for item in current_app.config.get("BILLING_ALLOWED_CURRENCIES", [])}
    if currency not in allowed_currencies:
        return _json_error("unsupported_currency", f"currency must be one of {sorted(allowed_currencies)}", 400)

    existing = PaymentTransaction.query.filter_by(user_id=g.current_user.id, idempotency_key=idem_key).first()
    if existing:
        return jsonify({"transaction_id": existing.id, "status": existing.status, "idempotent_replay": True}), 200

    provider_name = _active_provider_name()
    txn = PaymentTransaction(
        user_id=g.current_user.id,
        provider=provider_name,
        plan_code=plan_code,
        amount=amount,
        currency=currency,
        idempotency_key=idem_key,
        status="created",
    )
    db.session.add(txn)
    db.session.flush()

    try:
        provider = get_payment_provider(txn.provider)
        provider_response = provider.initiate_payment(
            ProviderInitiateRequest(
                transaction_id=txn.id,
                user_id=g.current_user.id,
                plan_code=plan_code,
                amount=amount,
                currency=currency,
                idempotency_key=idem_key,
                customer_email=getattr(g.current_user, "email", None),
                success_url=str(payload.get("success_url") or current_app.config.get("BILLING_CHECKOUT_SUCCESS_URL")),
                failure_url=str(payload.get("failure_url") or current_app.config.get("BILLING_CHECKOUT_FAILURE_URL")),
                callback_url=str(current_app.config.get("BILLING_CALLBACK_URL")),
                metadata=_metadata(payload),
            )
        )
    except ValueError as exc:
        txn.status = "provider_error"
        db.session.commit()
        return _json_error("unsupported_provider", str(exc), 400)
    except RuntimeError as exc:
        txn.status = "provider_not_configured"
        db.session.commit()
        return _json_error("provider_not_configured", str(exc), 503)

    txn.provider_payment_id = provider_response.provider_payment_id
    txn.provider_conversation_id = provider_response.provider_conversation_id
    txn.raw_payload_json = json.dumps(provider_response.raw_payload)
    txn.status = "pending"
    db.session.commit()

    return jsonify(
        {
            "transaction_id": txn.id,
            "status": txn.status,
            "provider": txn.provider,
            "provider_conversation_id": txn.provider_conversation_id,
            "checkout_url": provider_response.checkout_url,
            "provider_readiness": get_provider_readiness(txn.provider).to_dict(),
        }
    ), 202


@billing_bp.post("/callback/iyzico")
def iyzico_callback():
    return _handle_provider_callback("iyzico")


@billing_bp.post("/callback/<provider_name>")
def provider_callback(provider_name: str):
    return _handle_provider_callback(provider_name.strip().lower())


def _handle_provider_callback(provider_name: str):
    if not _billing_enabled():
        return _json_error("billing_disabled", "Billing is disabled", 501)

    payload = request.get_json(silent=True) or {}
    signature = request.headers.get("X-Iyzico-Signature") or request.headers.get("X-Payment-Signature")
    conversation_id = payload.get("conversationId")
    if not conversation_id:
        return jsonify({"code": "missing_conversation_id"}), 400

    txn = PaymentTransaction.query.filter_by(provider=provider_name, provider_conversation_id=conversation_id).first()
    if not txn:
        return jsonify({"code": "transaction_not_found"}), 404

    try:
        provider = get_payment_provider(provider_name)
    except ValueError as exc:
        return _json_error("unsupported_provider", str(exc), 400)

    event, duplicate = _record_payment_event(provider_name=provider_name, payload=payload, conversation_id=str(conversation_id))
    result = provider.verify_callback(payload=payload, signature=signature)
    txn.status = result.status if result.is_verified else "failed"
    txn.provider_payment_id = result.provider_payment_id or txn.provider_payment_id
    txn.raw_payload_json = json.dumps(result.raw_payload)
    event.processed_at = datetime.now(UTC)

    if result.is_verified and txn.status == "paid":
        _activate_subscription(txn)
    db.session.commit()

    return jsonify(
        {
            "transaction_id": txn.id,
            "verified": result.is_verified,
            "status": txn.status,
            "provider": provider_name,
            "event_id": event.event_id,
            "duplicate_event": duplicate,
            "failure_reason": result.failure_reason,
        }
    ), 200


def _record_payment_event(provider_name: str, payload: dict[str, Any], conversation_id: str) -> tuple[PaymentEvent, bool]:
    raw_event_id = payload.get("eventId") or payload.get("paymentId") or f"{conversation_id}:{payload.get('paymentStatus', 'unknown')}"
    event_id = f"{provider_name}:{raw_event_id}"
    existing = PaymentEvent.query.filter_by(event_id=event_id).first()
    if existing:
        return existing, True
    event = PaymentEvent(
        provider=provider_name,
        event_id=event_id,
        event_type=str(payload.get("eventType") or "payment.callback"),
        payload_json=payload,
    )
    db.session.add(event)
    db.session.flush()
    return event, False


def _activate_subscription(txn: PaymentTransaction) -> None:
    user = db.session.get(User, txn.user_id)
    if not user:
        return
    plan = Plan.query.filter_by(code=txn.plan_code).one_or_none()
    if plan:
        user.plan_id = plan.id
    user.subscription_status = "active"
    user.subscription_started_at = datetime.now(UTC)


def _metadata(payload: dict[str, Any]) -> dict[str, str]:
    raw_metadata = payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {}
    return {str(key): str(value) for key, value in raw_metadata.items()}
