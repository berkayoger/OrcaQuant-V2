# Environment Variables

## Required in production

- `SECRET_KEY`: Flask secret key.
- `CORS_ALLOWED_ORIGINS`: comma-separated explicit origins (required in production mode).
- `POSTGRES_PASSWORD`: database password used by `docker-compose.prod.yml`.

## Core app

- `FLASK_ENV`: `development|testing|production`.
- `DATABASE_URL`: SQLAlchemy URL.
- `JWT_ACCESS_TOKEN_MINUTES`: access token TTL.
- `JWT_REFRESH_TOKEN_DAYS`: refresh token TTL.
- `ENABLE_BILLING`: feature toggle.
- `ENABLE_REALTIME`: feature toggle.
- `MAX_CONTENT_LENGTH`: max payload bytes.

## Account lifecycle / verification codes

- `ACCOUNT_VERIFICATION_CODE_TTL_MINUTES`: how long login/email/password-reset codes remain valid.
- `ACCOUNT_VERIFICATION_MAX_ATTEMPTS`: failed attempts before a code is locked.
- `ACCOUNT_CODE_CHANNEL`: delivery channel boundary. Supported values: `email`, `sms`, `dev`.
- `ACCOUNT_CODE_DEBUG_RESPONSE`: when true, debug/test responses include the raw code. Must remain false in production.

Production guardrails:

- `ACCOUNT_CODE_DEBUG_RESPONSE=true` is blocked in production.
- A real email/SMS sender should be wired inside `VerificationDeliveryService`; routes should not import provider SDKs directly.

## Billing provider boundary

- `BILLING_PROVIDER`: active provider key. Supported values: `fake`, `iyzico`.
- `BILLING_ALLOWED_CURRENCIES`: comma-separated ISO-like currency allowlist, for example `TRY,USD,EUR`.
- `BILLING_CHECKOUT_SUCCESS_URL`: frontend URL users return to after successful checkout.
- `BILLING_CHECKOUT_FAILURE_URL`: frontend URL users return to after failed/cancelled checkout.
- `BILLING_CALLBACK_URL`: backend callback/webhook URL registered with the payment provider.
- `PAYMENT_PROVIDER_TIMEOUT_SECONDS`: outbound provider timeout for the future SDK/API call.

### Iyzico adapter

- `IYZICO_API_KEY`: Iyzico API key.
- `IYZICO_SECRET`: Iyzico secret/signing key.
- `IYZICO_BASE_URL`: Iyzico API base URL. Use the sandbox URL outside production.

Production guardrails:

- `BILLING_PROVIDER=fake` is blocked when `ENABLE_BILLING=true` and `FLASK_ENV=production`.
- `BILLING_PROVIDER=iyzico` requires `IYZICO_API_KEY`, `IYZICO_SECRET`, and `IYZICO_BASE_URL` in production.
- Checkout/callback URLs must be valid `http` or `https` URLs.

## Market data

- `MARKET_DATA_PROVIDER`
- `MARKET_DATA_TIMEOUT_SECONDS`
- `MARKET_DATA_CACHE_TTL_SECONDS`

## Rate limit / cache infrastructure

- `REDIS_URL`
- `RATE_LIMIT_STORAGE_URI`

## Gunicorn (optional overrides)

- `GUNICORN_BIND`
- `GUNICORN_WORKERS`
- `GUNICORN_WORKER_CLASS`
- `GUNICORN_TIMEOUT`
- `GUNICORN_KEEPALIVE`
- `GUNICORN_GRACEFUL_TIMEOUT`
- `GUNICORN_ACCESSLOG`
- `GUNICORN_ERRORLOG`
- `GUNICORN_LOG_LEVEL`
