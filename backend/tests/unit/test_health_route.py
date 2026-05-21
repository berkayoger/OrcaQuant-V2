def test_health_route_returns_ok(client):
    response = client.get("/api/v1/healthz")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_readiness_route_returns_ok(client):
    response = client.get("/api/v1/readyz")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "checks": {"database": "ok"}}


def test_readiness_route_returns_503_when_database_check_fails(client, monkeypatch):
    from app.api.v1 import health_routes

    def _raise(*args, **kwargs):
        raise RuntimeError("db down")

    monkeypatch.setattr(health_routes.db.session, "execute", _raise)

    response = client.get("/api/v1/readyz")

    assert response.status_code == 503
    assert response.get_json() == {"status": "error", "checks": {"database": "error"}}
