def test_auth_status(client):
    res = client.get('/api/v1/auth/status')
    assert res.status_code == 200
