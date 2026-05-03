import pytest

from app.core.errors.exceptions import AuthenticationError
from app.core.security.token_service import create_access_token, decode_access_token
from app.factory import create_app


def test_create_and_decode_access_token() -> None:
    app = create_app("testing")
    with app.app_context():
        token = create_access_token("user-1", {"role": "user"})
        payload = decode_access_token(token)

    assert payload["sub"] == "user-1"
    assert payload["type"] == "access"
    assert payload["role"] == "user"


def test_decode_invalid_token_raises_auth_error() -> None:
    app = create_app("testing")
    with app.app_context(), pytest.raises(AuthenticationError):
        decode_access_token("bad-token")
