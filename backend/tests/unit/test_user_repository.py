import pytest

from app.core.errors.exceptions import ValidationError
from app.repositories.user_repository import UserRepository


def test_repository_create_and_get_user(app):
    with app.app_context():
        repo = UserRepository()
        created = repo.create_user("repo@example.com", "hash")
        fetched = repo.get_by_email("repo@example.com")
        by_id = repo.get_by_id(created["id"])

        assert set(created.keys()) == {"id", "email", "password_hash", "role", "is_active"}
        assert fetched["email"] == "repo@example.com"
        assert by_id["id"] == created["id"]


def test_repository_prevents_duplicate_email(app):
    with app.app_context():
        repo = UserRepository()
        repo.create_user("dup-repo@example.com", "hash")
        with pytest.raises(ValidationError):
            repo.create_user("dup-repo@example.com", "hash2")
