from app.extensions import db
from app.models.account_verification_code import AccountVerificationCode
from app.models.user import User
from app.models.username_reservation import UsernameReservation


def _register(client, email="user@example.com", username="trader.one", password="Password123!"):
    return client.post(
        "/api/v1/auth/register",
        json={"email": email, "username": username, "password": password},
    )


def test_register_reserves_username_and_verifies_email(client, db_session):
    response = _register(client)

    assert response.status_code == 201
    data = response.get_json()
    assert data["user"]["username"] == "trader.one"
    assert data["user"]["is_email_verified"] is False
    code = data["verification"]["delivery"]["debug_code"]
    assert AccountVerificationCode.query.count() == 1
    assert UsernameReservation.query.filter_by(username="trader.one").count() == 1

    verify = client.post("/api/v1/auth/email/verify", json={"email": "user@example.com", "code": code})

    assert verify.status_code == 200
    user = User.query.filter_by(email="user@example.com").one()
    assert user.is_email_verified is True


def test_code_login_issues_tokens(client, db_session):
    _register(client, email="login-code@example.com", username="login.code")

    send = client.post("/api/v1/auth/login/code/send", json={"email": "login-code@example.com"})
    assert send.status_code == 202
    code = send.get_json()["delivery"]["debug_code"]

    login = client.post("/api/v1/auth/login/code", json={"email": "login-code@example.com", "code": code})

    assert login.status_code == 200
    data = login.get_json()
    assert data["access_token"]
    assert data["refresh_token"]
    assert data["user"]["username"] == "login.code"


def test_password_forgot_reset_and_stale_token_guard(client, db_session):
    registered = _register(client, email="reset@example.com", username="reset.user", password="OldPassword123!")
    old_access = registered.get_json()["access_token"]

    forgot = client.post("/api/v1/auth/password/forgot", json={"email": "reset@example.com"})
    assert forgot.status_code == 202
    code = forgot.get_json()["delivery"]["debug_code"]

    reset = client.post(
        "/api/v1/auth/password/reset",
        json={"email": "reset@example.com", "code": code, "new_password": "NewPassword123!"},
    )
    assert reset.status_code == 200

    stale = client.get("/api/v1/me/", headers={"Authorization": f"Bearer {old_access}"})
    assert stale.status_code == 401

    old_login = client.post("/api/v1/auth/login", json={"email": "reset@example.com", "password": "OldPassword123!"})
    assert old_login.status_code == 401

    new_login = client.post("/api/v1/auth/login", json={"email": "reset@example.com", "password": "NewPassword123!"})
    assert new_login.status_code == 200


def test_username_change_keeps_old_username_reserved(client, db_session):
    response = _register(client, email="namechange@example.com", username="alpha.name")
    token = response.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    change = client.patch("/api/v1/me/username", headers=headers, json={"username": "beta.name"})
    assert change.status_code == 200
    assert change.get_json()["username"] == "beta.name"

    old_available = client.get("/api/v1/auth/username/check?username=alpha.name")
    assert old_available.status_code == 200
    assert old_available.get_json()["available"] is False

    second = _register(client, email="second@example.com", username="alpha.name")
    assert second.status_code == 400

    claim_back = client.patch("/api/v1/me/username", headers=headers, json={"username": "alpha.name"})
    assert claim_back.status_code == 400
