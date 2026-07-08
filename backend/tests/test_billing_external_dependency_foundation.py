from app.core.security.token_service import create_access_token
from app.extensions import db
from app.models.payment import PaymentTransaction
from app.models.payment_event import PaymentEvent
from app.models.plan import Plan
from app.models.user import User


def _create_user_with_headers(email: str = "billing@example.com") -> tuple[User, dict[str, str]]:
    user = User(email=email, password_hash="hash")
    db.session.add(user)
    db.session.commit()
    token = create_access_token(user.id)
    return user, {"Authorization": f"Bearer {token}"}


def test_billing_status_reports_provider_readiness(app, client, db_session):
    app.config.update(
        ENABLE_BILLING=True,
        BILLING_PROVIDER="iyzico",
        IYZICO_API_KEY="",
        IYZICO_SECRET="",
        IYZICO_BASE_URL="https://sandbox-api.iyzipay.com",
    )

    response = client.get("/api/v1/billing/status")

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ready_for_external_binding"
    assert data["active_provider"] == "iyzico"
    assert data["active_provider_readiness"]["configured"] is False
    assert "IYZICO_API_KEY" in data["active_provider_readiness"]["missing_settings"]
    assert "fake" in data["supported_providers"]
    assert "iyzico" in data["supported_providers"]


def test_fake_billing_checkout_and_callback_flow(app, client, db_session):
    app.config.update(ENABLE_BILLING=True, BILLING_PROVIDER="fake")
    plan = Plan(code="pro", name="Pro")
    db.session.add(plan)
    db.session.commit()
    user, auth_headers = _create_user_with_headers()

    response = client.post(
        "/api/v1/billing/initiate",
        headers={**auth_headers, "Idempotency-Key": "billing-key-1"},
        json={"plan_code": "pro", "amount": "199.00", "currency": "TRY", "metadata": {"source": "pytest"}},
    )

    assert response.status_code == 202
    data = response.get_json()
    assert data["provider"] == "fake"
    assert data["provider_readiness"]["integration_status"] == "development_only"
    txn = db.session.get(PaymentTransaction, data["transaction_id"])
    assert txn.status == "pending"

    callback = client.post(
        "/api/v1/billing/callback/fake",
        json={
            "eventId": "evt-fake-paid-1",
            "mock_verified": True,
            "paymentStatus": "paid",
            "conversationId": data["provider_conversation_id"],
            "paymentId": txn.provider_payment_id,
        },
    )

    assert callback.status_code == 200
    callback_data = callback.get_json()
    assert callback_data["verified"] is True
    assert callback_data["status"] == "paid"
    assert callback_data["duplicate_event"] is False
    db.session.refresh(user)
    assert user.subscription_status == "active"
    assert user.plan_id == plan.id
    assert PaymentEvent.query.count() == 1


def test_idempotent_billing_initiation_reuses_transaction(app, client, db_session):
    app.config.update(ENABLE_BILLING=True, BILLING_PROVIDER="fake")
    _, auth_headers = _create_user_with_headers("billing-idempotency@example.com")

    first = client.post(
        "/api/v1/billing/initiate",
        headers={**auth_headers, "Idempotency-Key": "billing-key-2"},
        json={"plan_code": "pro", "amount": "99.00", "currency": "TRY"},
    )
    second = client.post(
        "/api/v1/billing/initiate",
        headers={**auth_headers, "Idempotency-Key": "billing-key-2"},
        json={"plan_code": "pro", "amount": "99.00", "currency": "TRY"},
    )

    assert first.status_code == 202
    assert second.status_code == 200
    assert second.get_json()["idempotent_replay"] is True
    assert PaymentTransaction.query.count() == 1
