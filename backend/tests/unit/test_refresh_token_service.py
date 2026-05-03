from app.core.security.refresh_token_service import generate_refresh_token, hash_refresh_token, verify_refresh_token


def test_refresh_token_hash_and_verify() -> None:
    token = generate_refresh_token()
    token_hash = hash_refresh_token(token)

    assert token_hash != token
    assert verify_refresh_token(token, token_hash) is True
    assert verify_refresh_token("invalid", token_hash) is False
