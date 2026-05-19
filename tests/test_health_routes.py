def test_health(client):
    res = client.get('/api/v1/healthz')
    assert res.status_code == 200
