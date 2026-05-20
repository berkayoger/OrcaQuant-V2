from app.models.session import Session
from app.services.plans.seed_plans import seed_plans


def test_seed_plans_idempotent(app):
    with app.app_context():
        first = seed_plans()
        second = seed_plans()
        assert first["plans"] >= 1
        assert second["plans"] == 0
        assert second["limits"] == 0


def test_register_assigns_free_plan_when_seeded(client, app):
    with app.app_context():
        seed_plans()
    res = client.post("/api/v1/auth/register", json={"email": "plan@example.com", "password": "Password123"})
    assert res.status_code == 201
    body = res.get_json()
    assert body["user"]["plan_code"] == "free"


def test_missing_refresh_token_returns_400(client):
    res = client.post("/api/v1/auth/refresh", json={})
    assert res.status_code == 400
    assert res.get_json()["error"]["code"] == "missing_refresh_token"


def test_invalid_refresh_token_returns_401(client):
    res = client.post("/api/v1/auth/refresh", json={"refresh_token": "not-a-jwt"})
    assert res.status_code == 401


def test_logout_then_refresh_fails(client):
    reg = client.post("/api/v1/auth/register", json={"email": "revoke@example.com", "password": "Password123"}).get_json()
    token = reg["refresh_token"]
    out = client.post("/api/v1/auth/logout", json={"refresh_token": token})
    assert out.status_code == 200
    refreshed = client.post("/api/v1/auth/refresh", json={"refresh_token": token})
    assert refreshed.status_code == 401


def test_register_and_login_create_session_rows(client, app):
    reg = client.post("/api/v1/auth/register", json={"email": "sess@example.com", "password": "Password123"})
    assert reg.status_code == 201
    login = client.post("/api/v1/auth/login", json={"email": "sess@example.com", "password": "Password123"})
    assert login.status_code == 200
    with app.app_context():
        sessions = Session.query.all()
        assert len(sessions) == 2


def test_refresh_token_not_stored_raw(client, app):
    reg = client.post("/api/v1/auth/register", json={"email": "hash@example.com", "password": "Password123"}).get_json()
    raw = reg["refresh_token"]
    with app.app_context():
        session = Session.query.one()
        assert session.refresh_token_hash != raw
