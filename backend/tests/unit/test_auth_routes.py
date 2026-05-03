def test_register_route_returns_access_token(client) -> None:
    response = client.post("/api/v1/auth/register", json={"email": "route@example.com", "password": "Password123"})
    assert response.status_code == 201
    body = response.get_json()
    assert "access_token" in body
    assert "password_hash" not in body


def test_login_route_valid_and_invalid_credentials(client) -> None:
    client.post("/api/v1/auth/register", json={"email": "route2@example.com", "password": "Password123"})
    ok = client.post("/api/v1/auth/login", json={"email": "route2@example.com", "password": "Password123"})
    bad = client.post("/api/v1/auth/login", json={"email": "route2@example.com", "password": "WrongPass123"})

    assert ok.status_code == 200
    assert "access_token" in ok.get_json()
    assert "password_hash" not in ok.get_json()
    assert bad.status_code == 401
    assert bad.get_json()["error"]["message"] == "Invalid email or password"


def test_register_duplicate_email_fails(client) -> None:
    client.post("/api/v1/auth/register", json={"email": "dup@example.com", "password": "Password123"})
    second = client.post("/api/v1/auth/register", json={"email": "dup@example.com", "password": "Password123"})
    assert second.status_code == 400
