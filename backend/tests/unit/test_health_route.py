def test_health_route_returns_ok(client):
    response = client.get("/api/v1/healthz")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_readiness_route_returns_ok(client):
    response = client.get("/api/v1/readyz")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "checks": {"database": "ok"}}
