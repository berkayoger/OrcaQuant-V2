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

## Admin Usage Contract (V2)
- `GET /api/v1/admin/usage` (admin-only): paginated usage rows, supports `user_id` filter.
- `POST /api/v1/admin/usage` (admin-only): create usage row with `user_id`, `feature_key`, `used_count`.

## Billing Provider Foundation (V2)
- Configurable provider selection via `BILLING_PROVIDER` (`fake` default, `iyzico` optional).
- Fake provider is deterministic and test-only friendly.
