from app.core.security.token_service import create_access_token, decode_refresh_token


class RefreshService:
    def execute(self, refresh_token: str) -> dict:
        payload = decode_refresh_token(refresh_token)
        return {"access_token": create_access_token(payload["sub"]), "token_type": "bearer"}
