from app.models.session import Session


def _register(client, email: str):
    return client.post("/api/v1/auth/register", json={"email": email, "password": "Password123"})


def test_refresh_missing_refresh_token_returns_400_json(client):
    res = client.post("/api/v1/auth/refresh", json={})
    assert res.status_code == 400
    assert res.get_json() == {"status": "error", "code": "missing_refresh_token"}


def test_refresh_invalid_refresh_token_returns_401_json_shape(client):
    res = client.post("/api/v1/auth/refresh", json={"refresh_token": "bad.token"})
    assert res.status_code == 401
    assert "error" in res.get_json()


def test_logout_missing_refresh_token_returns_400_json(client):
    res = client.post("/api/v1/auth/logout", json={})
    assert res.status_code == 400
    assert res.get_json() == {"status": "error", "code": "missing_refresh_token"}


def test_logout_invalid_refresh_token_returns_401_json_shape(client):
    res = client.post("/api/v1/auth/logout", json={"refresh_token": "bad.token"})
    assert res.status_code == 401
    assert "error" in res.get_json()


def test_refresh_after_logout_returns_401(client):
    reg = _register(client, "edge-logout@example.com").get_json()
    token = reg["refresh_token"]
    assert client.post("/api/v1/auth/logout", json={"refresh_token": token}).status_code == 200
    refreshed = client.post("/api/v1/auth/refresh", json={"refresh_token": token})
    assert refreshed.status_code == 401


def test_register_and_login_create_session_rows(client, app):
    _register(client, "session-check@example.com")
    client.post("/api/v1/auth/login", json={"email": "session-check@example.com", "password": "Password123"})
    with app.app_context():
        assert Session.query.count() == 2


def test_refresh_token_hash_not_equal_raw_token(client, app):
    raw = _register(client, "hash-check@example.com").get_json()["refresh_token"]
    with app.app_context():
        row = Session.query.one()
        assert row.refresh_token_hash != raw


def test_refresh_response_contract_without_new_refresh_token(client):
    auth = _register(client, "refresh-contract@example.com").get_json()
    refreshed = client.post("/api/v1/auth/refresh", json={"refresh_token": auth["refresh_token"]})
    body = refreshed.get_json()
    assert refreshed.status_code == 200
    assert {"access_token", "token_type", "user"}.issubset(body.keys())
    assert "refresh_token" not in body
