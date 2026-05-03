import pytest

from app.core.errors.exceptions import AuthenticationError
from app.repositories.user_repository import UserRepository
from app.services.auth.login_service import LoginService
from app.services.auth.register_service import RegisterService


def test_register_and_login_services(app) -> None:
    with app.app_context():
        repo = UserRepository()
        register_service = RegisterService(repo)
        login_service = LoginService(repo)

        registered = register_service.execute({"email": "user@example.com", "password": "Password123"})
        logged_in = login_service.execute({"email": "user@example.com", "password": "Password123"})

        assert registered["access_token"]
        assert logged_in["access_token"]


def test_login_invalid_credentials(app) -> None:
    with app.app_context():
        repo = UserRepository()
        register_service = RegisterService(repo)
        login_service = LoginService(repo)
        register_service.execute({"email": "user@example.com", "password": "Password123"})

        with pytest.raises(AuthenticationError):
            login_service.execute({"email": "user@example.com", "password": "WrongPass123"})
