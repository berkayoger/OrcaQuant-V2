from app.models.session import Session


def test_register_login_refresh_logout_flow(client):
    reg = client.post('/api/v1/auth/register', json={"email": "user@example.com", "password": "password123"})
    assert reg.status_code == 201
    rj = reg.get_json()
    assert rj["access_token"] and rj["refresh_token"] and rj["user"]["id"]

    login = client.post('/api/v1/auth/login', json={"email": "user@example.com", "password": "password123"})
    assert login.status_code == 200
    lj = login.get_json()
    assert lj["access_token"] and lj["refresh_token"] and lj["user"]["email"] == "user@example.com"

    session = Session.query.filter_by(jti=None).first()
    assert session is None

    refresh = client.post('/api/v1/auth/refresh', json={"refresh_token": lj["refresh_token"]})
    assert refresh.status_code == 200
    refreshed = refresh.get_json()
    assert refreshed["access_token"]
    assert refreshed["refresh_token"]
    assert refreshed["refresh_token"] != lj["refresh_token"]

    sessions = Session.query.filter_by(user_id=lj["user"]["id"]).all()
    assert len(sessions) == 2
    assert len([s for s in sessions if s.is_active]) == 1

    reuse = client.post('/api/v1/auth/refresh', json={"refresh_token": lj["refresh_token"]})
    assert reuse.status_code == 401
    assert reuse.get_json()["error"]["code"] == "refresh_token_reuse_detected"

    assert Session.query.filter_by(user_id=lj["user"]["id"], is_active=True).count() == 0

    relogin = client.post('/api/v1/auth/login', json={"email": "user@example.com", "password": "password123"})
    rj2 = relogin.get_json()
    logout = client.post('/api/v1/auth/logout', json={"refresh_token": rj2["refresh_token"]})
    assert logout.status_code == 200
    refresh2 = client.post('/api/v1/auth/refresh', json={"refresh_token": rj2["refresh_token"]})
    assert refresh2.status_code == 401


def test_refresh_missing_and_invalid_token(client):
    missing = client.post('/api/v1/auth/refresh', json={})
    assert missing.status_code == 400
    assert missing.get_json()["error"]["code"] == "missing_refresh_token"

    invalid = client.post('/api/v1/auth/refresh', json={"refresh_token": "bad.token.value"})
    assert invalid.status_code == 401
    assert invalid.get_json()["error"]["code"] in {"token_invalid", "token_expired"}


def test_refresh_hash_storage_and_rotation_works(client):
    reg = client.post('/api/v1/auth/register', json={"email": "rot@example.com", "password": "password123"}).get_json()
    user_id = reg["user"]["id"]
    s1 = Session.query.filter_by(user_id=user_id, is_active=True).first()
    assert s1 is not None
    assert s1.refresh_token_hash != reg["refresh_token"]

    r1 = client.post('/api/v1/auth/refresh', json={"refresh_token": reg["refresh_token"]})
    assert r1.status_code == 200
    new_rt = r1.get_json()["refresh_token"]
    r2 = client.post('/api/v1/auth/refresh', json={"refresh_token": new_rt})
    assert r2.status_code == 200
