def test_health(client):
    res = client.get('/api/v1/health')
    assert res.status_code == 200
