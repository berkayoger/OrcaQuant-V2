# API Contracts
## AuthResponse
```json
{
  "access_token": "...",
  "refresh_token": "...",
  "token_type": "bearer",
  "user": {"id":"...","email":"...","role":"user","plan_code":"free"}
}
```

## Billing
- `GET /api/v1/billing/status` -> enabled flag.
- `POST /api/v1/billing/initiate` -> 501 when disabled or not implemented.
