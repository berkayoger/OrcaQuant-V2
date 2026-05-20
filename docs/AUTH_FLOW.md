# Auth Flow
- `POST /api/v1/auth/register`: creates user, assigns `free` plan if seeded, returns `AuthResponse`.
- `POST /api/v1/auth/login`: validates credentials, returns `AuthResponse`.
- `POST /api/v1/auth/refresh`: requires `refresh_token`; validates token type, jti, active session, hashed token match, active user.
- `POST /api/v1/auth/logout`: revokes matching refresh session by jti.

## Session strategy
Refresh tokens are never stored raw. DB stores SHA-256 hash and jti in `sessions`.

## TODO
Refresh token rotation/reuse-detection hardening.
