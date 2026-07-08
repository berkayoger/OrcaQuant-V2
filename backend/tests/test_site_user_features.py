from app.models.session import Session
from app.models.user import User
from app.models.user_profile import UserProfile


def _register(client, email="site-user@example.com", username="site.user", password="Password123!"):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": email, "username": username, "password": password},
    )
    assert response.status_code == 201
    token = response.get_json()["access_token"]
    return response.get_json(), {"Authorization": f"Bearer {token}"}


def test_profile_settings_home_and_export_flow(client, db_session):
    _, headers = _register(client)

    profile = client.patch(
        "/api/v1/profile/",
        headers=headers,
        json={
            "display_name": "Site User",
            "bio": "Long-term risk aware trader",
            "risk_profile": "aggressive",
            "preferred_horizon_days": 90,
            "max_drawdown_tolerance": 0.35,
            "capital": "25000.50",
        },
    )
    assert profile.status_code == 200
    profile_data = profile.get_json()["data"]
    assert profile_data["display_name"] == "Site User"
    assert profile_data["risk_profile"] == "AGGRESSIVE"
    assert profile_data["capital"] == 25000.5

    settings = client.patch(
        "/api/v1/settings/",
        headers=headers,
        json={
            "theme": "dark",
            "preferred_currency": "TRY",
            "notification_preferences": {"email": True, "daily_brief": False},
            "privacy": {"analytics_opt_in": True},
        },
    )
    assert settings.status_code == 200
    settings_data = settings.get_json()["data"]
    assert settings_data["theme"] == "dark"
    assert settings_data["preferred_currency"] == "TRY"
    assert settings_data["notification_preferences"]["email"] is True
    assert settings_data["notification_preferences"]["daily_brief"] is False
    assert settings_data["privacy"]["analytics_opt_in"] is True

    home = client.get("/api/v1/me/home", headers=headers)
    assert home.status_code == 200
    home_data = home.get_json()["data"]
    assert home_data["user"]["display_name"] == "Site User"
    assert home_data["summary"]["profile_completion_percent"] >= 40
    assert any(action["key"] in {"verify_email", "add_watchlist", "create_alert"} for action in home_data["quick_actions"])

    export = client.get("/api/v1/me/export", headers=headers)
    assert export.status_code == 200
    export_data = export.get_json()["data"]
    assert export_data["account"]["email"] == "site-user@example.com"
    assert export_data["profile"]["display_name"] == "Site User"
    assert "sessions" in export_data


def test_session_management_and_password_change(client, db_session):
    _, headers = _register(client, email="security@example.com", username="security.user", password="OldPassword123!")

    sessions = client.get("/api/v1/me/sessions", headers=headers)
    assert sessions.status_code == 200
    items = sessions.get_json()["data"]["items"]
    assert len(items) == 1
    session_id = items[0]["id"]

    revoke = client.delete(f"/api/v1/me/sessions/{session_id}", headers=headers)
    assert revoke.status_code == 200
    assert Session.query.filter_by(id=session_id).one().is_active is False

    relogin = client.post("/api/v1/auth/login", json={"email": "security@example.com", "password": "OldPassword123!"})
    assert relogin.status_code == 200
    token = relogin.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    change = client.patch(
        "/api/v1/me/password",
        headers=headers,
        json={"current_password": "OldPassword123!", "new_password": "NewPassword123!"},
    )
    assert change.status_code == 200

    old_login = client.post("/api/v1/auth/login", json={"email": "security@example.com", "password": "OldPassword123!"})
    assert old_login.status_code == 401
    new_login = client.post("/api/v1/auth/login", json={"email": "security@example.com", "password": "NewPassword123!"})
    assert new_login.status_code == 200


def test_account_deactivation_revokes_access(client, db_session):
    _, headers = _register(client, email="deactivate@example.com", username="deactivate.user", password="Password123!")

    response = client.post("/api/v1/me/deactivate", headers=headers, json={"password": "Password123!"})

    assert response.status_code == 200
    user = User.query.filter_by(email="deactivate@example.com").one()
    assert user.is_active is False
    assert Session.query.filter_by(user_id=user.id, is_active=True).count() == 0

    after = client.get("/api/v1/me/", headers=headers)
    assert after.status_code == 401


def test_onboarding_endpoint_updates_profile_and_settings(client, db_session):
    _, headers = _register(client, email="onboarding@example.com", username="onboarding.user")

    response = client.post(
        "/api/v1/profile/onboarding",
        headers=headers,
        json={
            "display_name": "Onboarding User",
            "risk_profile": "conservative",
            "preferred_horizon_days": 14,
            "max_drawdown_tolerance": 0.1,
            "preferred_currency": "EUR",
            "timezone": "Europe/Istanbul",
        },
    )

    assert response.status_code == 200
    profile = UserProfile.query.filter_by(user_id=response.get_json()["data"]["profile"]["user_id"]).one()
    assert profile.display_name == "Onboarding User"
    assert profile.risk_profile == "CONSERVATIVE"
    assert profile.preferred_currency == "EUR"
