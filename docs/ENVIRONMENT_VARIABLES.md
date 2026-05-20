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
