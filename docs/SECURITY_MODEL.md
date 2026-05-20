# Security Model

- JWT access + refresh flow with hashed refresh-session storage.
- Generic JSON 500 handler prevents leaking exception internals.
- Usage guards and auth guards are fail-closed for protected features.
- Billing and realtime are disabled-by-default safety posture.
