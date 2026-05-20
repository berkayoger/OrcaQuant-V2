# API Contracts

## AuthResponse
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "user": {"id": "...", "email": "...", "role": "...", "plan_code": "free"}
}
```

## Billing status
- `GET /api/v1/billing/status` => disabled by default.

## Realtime status
- `GET /api/v1/market/realtime/status` => disabled by default or not_implemented.
