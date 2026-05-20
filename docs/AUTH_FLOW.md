# Auth Flow

- Register/Login return `access_token`, `refresh_token`, `token_type`, `user`.
- A hashed refresh-token session is created at register/login.
- Refresh validates JWT + active session + hash match.
- Logout revokes session by refresh-token `jti`.
- Missing refresh token => 400. Invalid/expired/revoked => 401 JSON.

## Known gap
- TODO(v1-migration): refresh token rotation + reuse detection.
