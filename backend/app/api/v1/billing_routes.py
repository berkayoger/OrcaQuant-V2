from __future__ import annotations

import json
from decimal import Decimal, InvalidOperation

from flask import Blueprint, current_app, g, jsonify, request

from app.core.security.auth_guard import require_auth
from app.extensions import db
from app.models.payment import PaymentTransaction
from app.models.user import User
from app.payments.provider_base import ProviderInitiateRequest
from app.payments.provider_factory import get_payment_provider

billing_bp = Blueprint("billing", __name__)


def _billing_enabled() -> bool:
    return bool(current_app.config.get("ENABLE_BILLING", False))


@billing_bp.get("/status")
def get_billing_status():
    enabled = _billing_enabled()
    return jsonify({"module": "billing", "enabled": enabled, "status": "skeleton" if enabled else "disabled"}), 200


@billing_bp.post("/initiate")
@require_auth
def initiate_billing():
    if not _billing_enabled():
        return jsonify({"code": "billing_disabled", "message": "Billing is disabled"}), 501

    idem_key = request.headers.get("Idempotency-Key", "").strip()
    if not idem_key:
        return jsonify({"code": "missing_idempotency_key", "message": "Idempotency-Key header is required"}), 400

    payload = request.get_json(silent=True) or {}
    plan_code = str(payload.get("plan_code") or "").strip()
    amount_raw = payload.get("amount")
    currency = str(payload.get("currency") or "TRY").strip().upper()
    if not plan_code:
        return jsonify({"code": "invalid_plan_code", "message": "plan_code is required"}), 400
    try:
        amount = Decimal(str(amount_raw))
    except (InvalidOperation, TypeError):
        return jsonify({"code": "invalid_amount", "message": "amount must be numeric"}), 400

    existing = PaymentTransaction.query.filter_by(user_id=g.current_user.id, idempotency_key=idem_key).first()
    if existing:
        return jsonify({"transaction_id": existing.id, "status": existing.status, "idempotent_replay": True}), 200

    txn = PaymentTransaction(
        user_id=g.current_user.id,
        provider=current_app.config.get("BILLING_PROVIDER", "fake").lower(),
        plan_code=plan_code,
        amount=amount,
        currency=currency,
        idempotency_key=idem_key,
        status="created",
    )
    db.session.add(txn)
    db.session.flush()

    provider = get_payment_provider(txn.provider)
    provider_response = provider.initiate_payment(
        ProviderInitiateRequest(
            transaction_id=txn.id,
            user_id=g.current_user.id,
            plan_code=plan_code,
            amount=amount,
            currency=currency,
            idempotency_key=idem_key,
        )
    )

    txn.provider_payment_id = provider_response.provider_payment_id
    txn.provider_conversation_id = provider_response.provider_conversation_id
    txn.raw_payload_json = json.dumps(provider_response.raw_payload)
    txn.status = "pending"
    db.session.commit()

    return jsonify({
        "transaction_id": txn.id,
        "status": txn.status,
        "provider": txn.provider,
        "checkout_url": provider_response.checkout_url,
    }), 202


@billing_bp.post("/callback/iyzico")
def iyzico_callback():
    if not _billing_enabled():
        return jsonify({"code": "billing_disabled", "message": "Billing is disabled"}), 501

    payload = request.get_json(silent=True) or {}
    signature = request.headers.get("X-Iyzico-Signature")
    conversation_id = payload.get("conversationId")
    if not conversation_id:
        return jsonify({"code": "missing_conversation_id"}), 400

    txn = PaymentTransaction.query.filter_by(provider=current_app.config.get("BILLING_PROVIDER", "fake").lower(), provider_conversation_id=conversation_id).first()
    if not txn:
        return jsonify({"code": "transaction_not_found"}), 404

    provider = get_payment_provider("iyzico")
    result = provider.verify_callback(payload=payload, signature=signature)
    txn.status = result.status if result.is_verified else "failed"
    txn.provider_payment_id = result.provider_payment_id or txn.provider_payment_id
    txn.raw_payload_json = json.dumps(result.raw_payload)

    if result.is_verified and txn.status == "paid":
        user = db.session.get(User, txn.user_id)
        if user:
            user.subscription_status = "active"
    db.session.commit()

    return jsonify({"transaction_id": txn.id, "verified": result.is_verified, "status": txn.status}), 200
