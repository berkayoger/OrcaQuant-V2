def _register_and_login(client):
    client.post('/api/v1/auth/register', json={"email": "usage@example.com", "password": "password123"})
    lj = client.post('/api/v1/auth/login', json={"email": "usage@example.com", "password": "password123"}).get_json()
    return {"Authorization": f"Bearer {lj['access_token']}"}


def test_me_usage_requires_auth(client):
    res = client.get('/api/v1/me/usage?feature_key=technical_analysis')
    assert res.status_code == 401


def test_me_usage_returns_current_user(client):
    headers = _register_and_login(client)
    res = client.get('/api/v1/me/usage?feature_key=technical_analysis', headers=headers)
    assert res.status_code == 200
    assert res.get_json()["feature_key"] == "technical_analysis"
