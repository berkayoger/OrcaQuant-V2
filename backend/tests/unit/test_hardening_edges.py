from flask import Blueprint

from app.extensions import db
from app.models.plan import Plan
from app.models.session import Session
from app.models.usage import DailyUsage, FeatureLimit
from app.models.user import User
from app.services.plans.seed_plans import seed_plans
from app.services.usage.usage_service import UsageService


def _auth_headers(client, email: str):
    reg = client.post("/api/v1/auth/register", json={"email": email, "password": "Password123"}).get_json()
    return {"Authorization": f"Bearer {reg['access_token']}"}, reg["refresh_token"]


def test_model_registry_has_critical_tables(app):
    with app.app_context():
        tables = set(db.metadata.tables.keys())
    required = {
        "users", "sessions", "api_keys", "plans", "feature_limits", "daily_usage",
        "payment_transactions", "promo_codes", "audit_events", "assets", "market_prices",
        "analysis_results", "decision_results", "risk_results",
    }
    assert required.issubset(tables)


def test_usage_service_status_shapes(app):
    with app.app_context():
        seed_plans()
        user = User(email="u@x.com", password_hash="x", plan_id=None)
        db.session.add(user)
        db.session.commit()
        svc = UsageService()
        s1 = svc.get_status(user.id, "technical_analysis")
        assert s1["quota"] is None and s1["limit_exists"] is False

        free = Plan.query.filter_by(code="free").one()
        user.plan_id = free.id
        db.session.commit()
        FeatureLimit.query.filter_by(plan_id=free.id, feature_key="technical_analysis").delete()
        db.session.commit()
        s2 = svc.get_status(user.id, "technical_analysis", free.id)
        assert s2["limit_exists"] is False

        fl = FeatureLimit(plan_id=free.id, feature_key="technical_analysis", enabled=False, daily_quota=0)
        db.session.add(fl)
        db.session.commit()
        s3 = svc.get_status(user.id, "technical_analysis", free.id)
        assert s3["feature_enabled"] is False

        fl.enabled = True
        fl.daily_quota = 4
        db.session.add(DailyUsage(user_id=user.id, feature_key="technical_analysis", used_count=3))
        db.session.commit()
        s4 = svc.get_status(user.id, "technical_analysis", free.id)
        assert s4["percent"] == 75 and s4["warn75"] is True and s4["warn90"] is False and s4["exhausted"] is False


def test_auth_refresh_logout_and_sessions(client, app):
    headers, refresh_token = _auth_headers(client, "authhard@example.com")
    assert client.post("/api/v1/auth/refresh", json={}).status_code == 400
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": "bad"}).status_code == 401

    with app.app_context():
        assert Session.query.count() == 1

    assert client.post("/api/v1/auth/logout", json={"refresh_token": "bad"}).status_code == 401
    assert client.post("/api/v1/auth/logout", json={"refresh_token": refresh_token}).status_code == 200
    assert client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token}).status_code == 401


def test_billing_and_realtime_statuses(client, app):
    resp = client.get("/api/v1/billing/status")
    assert resp.get_json()["enabled"] is False
    assert client.post("/api/v1/billing/initiate", json={}).status_code == 401

    headers, _ = _auth_headers(client, "billx@example.com")
    assert client.post("/api/v1/billing/initiate", headers=headers, json={}).get_json()["code"] == "billing_disabled"

    app.config["ENABLE_BILLING"] = True
    resp2 = client.post("/api/v1/billing/initiate", headers=headers, json={})
    assert resp2.status_code == 501 and resp2.get_json()["code"] == "not_implemented"

    app.config["ENABLE_REALTIME"] = False
    assert client.get("/api/v1/market/realtime/status").get_json()["status"] == "disabled"
    app.config["ENABLE_REALTIME"] = True
    assert client.get("/api/v1/market/realtime/status").get_json()["status"] == "not_implemented"


def test_generic_500_json_handler(app, client):
    bp = Blueprint("boom", __name__)

    @bp.get("/_boom")
    def _boom():
        raise RuntimeError("sensitive")

    app.register_blueprint(bp)
    resp = client.get("/_boom")
    assert resp.status_code == 500
    assert resp.get_json()["error"]["code"] == "internal_server_error"
