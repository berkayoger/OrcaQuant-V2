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
    assert refresh.get_json()["access_token"]

    logout = client.post('/api/v1/auth/logout', json={"refresh_token": lj["refresh_token"]})
    assert logout.status_code == 200

    refresh2 = client.post('/api/v1/auth/refresh', json={"refresh_token": lj["refresh_token"]})
    assert refresh2.status_code == 401
