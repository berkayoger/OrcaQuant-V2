# Security Model

- JWT access + refresh flow with hashed refresh-session storage.
- Refresh token rotation is enforced: every refresh invalidates the previous refresh token/session.
- Refresh token reuse detection revokes all active sessions for the user when a revoked/inactive token is reused.
- Stored refresh-session material is limited to SHA-256 hash + `jti` metadata (no raw refresh tokens at rest).
- Generic JSON 500 handler prevents leaking exception internals.
- Usage guards and auth guards are fail-closed for protected features.
- Billing and realtime are disabled-by-default safety posture.

## Future hardening
- Device/session listing UI + API
- Suspicious login/reuse alerting
- Refresh token family tracking
- Admin-driven session revocation tooling
