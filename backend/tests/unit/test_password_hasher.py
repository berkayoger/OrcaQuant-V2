import pytest

from app.core.errors.exceptions import ValidationError
from app.core.security.password_hasher import hash_password, verify_password


def test_hash_and_verify_password() -> None:
    hashed = hash_password("Password123")
    assert hashed != "Password123"
    assert verify_password("Password123", hashed) is True


def test_wrong_password_fails() -> None:
    hashed = hash_password("Password123")
    assert verify_password("WrongPassword", hashed) is False


def test_empty_password_rejected() -> None:
    with pytest.raises(ValidationError):
        hash_password("")
