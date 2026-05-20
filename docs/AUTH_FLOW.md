# Auth Flow

- Register/Login return `access_token`, `refresh_token`, `token_type`, `user`.
- A hashed refresh-token session is created at register/login.
- Refresh now rotates tokens on every successful use (old session revoked, new session created).
- Refresh validates JWT + session lookup + hash match + active user.
- Reusing a revoked/inactive refresh token is treated as reuse detection and revokes all active sessions for that user.
- Logout revokes session by refresh-token `jti`.
- Missing refresh token => 400. Invalid/expired/revoked => 401 JSON.
- Raw refresh tokens are never stored; only `jti` and SHA-256 `refresh_token_hash` are persisted.
