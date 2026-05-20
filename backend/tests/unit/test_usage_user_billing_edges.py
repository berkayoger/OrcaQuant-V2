from flask import jsonify

from app.models.plan import Plan
from app.models.usage import DailyUsage, FeatureLimit
from app.models.user import User
from app.services.plans.seed_plans import seed_plans


def _auth_headers(client, email: str):
    reg = client.post("/api/v1/auth/register", json={"email": email, "password": "Password123"}).get_json()
    return {"Authorization": f"Bearer {reg['access_token']}"}


def test_me_requires_auth(client):
    assert client.get("/api/v1/me/").status_code == 401


def test_me_returns_authenticated_user(client):
    headers = _auth_headers(client, "me@example.com")
    body = client.get("/api/v1/me/", headers=headers).get_json()
    assert body["email"] == "me@example.com"


def test_me_usage_payload(client):
    headers = _auth_headers(client, "usage@example.com")
    body = client.get("/api/v1/me/usage?feature_key=technical_analysis&user_id=other", headers=headers).get_json()
    for key in ["feature_key", "used", "quota", "remaining", "percent", "warn75", "warn90", "exhausted"]:
        assert key in body


def test_billing_status_disabled(client):
    resp = client.get("/api/v1/billing/status")
    assert resp.status_code == 200
    assert resp.get_json()["enabled"] is False


def test_billing_initiate_requires_auth(client):
    assert client.post("/api/v1/billing/initiate", json={}).status_code == 401


def test_billing_initiate_disabled(client):
    headers = _auth_headers(client, "bill@example.com")
    resp = client.post("/api/v1/billing/initiate", headers=headers, json={})
    assert resp.status_code == 501
    assert resp.get_json()["code"] == "billing_disabled"


def test_usage_guard_statuses(client, app):
    from app.core.security.auth_guard import require_auth
    from app.core.security.usage_guard import enforce_usage_limit

    @require_auth
    @enforce_usage_limit("technical_analysis")
    def ok_handler():
        return jsonify({"ok": True}), 200

    @require_auth
    @enforce_usage_limit("technical_analysis")
    def fail_handler():
        return jsonify({"ok": False}), 500

    app.add_url_rule("/_test/protected-ok", "protected_ok", ok_handler, methods=["GET"])
    app.add_url_rule("/_test/protected-fail", "protected_fail", fail_handler, methods=["GET"])

    assert client.get("/_test/protected-ok").status_code == 401

    headers_np = _auth_headers(client, "noplan@example.com")
    assert client.get("/_test/protected-ok", headers=headers_np).get_json()["error"]["code"] == "plan_required"

    with app.app_context():
        seed_plans()
    headers = _auth_headers(client, "planuser@example.com")

    with app.app_context():
        user = User.query.filter_by(email="planuser@example.com").one()
        free = Plan.query.filter_by(code="free").one()
        FeatureLimit.query.filter_by(plan_id=free.id, feature_key="technical_analysis").delete()
        assert user.plan_id == free.id
    resp = client.get("/_test/protected-ok", headers=headers)
    assert resp.status_code == 403
    assert resp.get_json()["error"]["code"] == "feature_not_configured"

    with app.app_context():
        limit = FeatureLimit(plan_id=free.id, feature_key="technical_analysis", enabled=False, daily_quota=0)
        from app.extensions import db
        db.session.add(limit)
        db.session.commit()
    resp = client.get("/_test/protected-ok", headers=headers)
    assert resp.status_code == 403
    assert resp.get_json()["error"]["code"] == "feature_disabled"

    with app.app_context():
        limit = FeatureLimit.query.filter_by(plan_id=free.id, feature_key="technical_analysis").one()
        limit.enabled = True
        limit.daily_quota = 1
        from app.extensions import db
        db.session.commit()

    first = client.get("/_test/protected-ok", headers=headers)
    second = client.get("/_test/protected-ok", headers=headers)
    assert first.status_code == 200
    assert second.status_code == 429
    assert second.get_json()["error"]["code"] == "quota_exceeded"

    before = int(first.headers["X-Usage-Used"])
    failed = client.get("/_test/protected-fail", headers=headers)
    assert failed.status_code == 500
    after = client.get("/api/v1/me/usage?feature_key=technical_analysis", headers=headers).get_json()["used"]
    assert after == before

    assert first.headers["X-Usage-Quota"] == "1"
