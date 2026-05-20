# Production Deployment (V2)

This repository now includes production-oriented deployment assets aligned with V1 maturity.

## Production stack files

- `docker-compose.prod.yml`: production compose stack with `postgres`, `redis`, `backend` (Gunicorn), and `nginx` reverse proxy.
- `backend/gunicorn.conf.py`: production Gunicorn runtime tuning (workers, timeouts, logs via env vars).
- `infra/nginx/nginx.prod.conf`: reverse proxy example routing requests to backend container.

## Local vs production

### Local (`docker-compose.yml`)
- Exposes backend and frontend development ports directly.
- Uses dev server flows (`flask run`, Vite dev server behavior).
- Optimized for iteration.

### Production (`docker-compose.prod.yml`)
- Runs Flask app behind Gunicorn.
- Places Nginx in front of backend.
- Adds restart policy and persistent redis/postgres volumes.
- Uses readiness/health endpoints for operational checks.

## Deployment steps (generic, non-cloud-specific)

1. Create `.env` with production values (see `docs/ENVIRONMENT_VARIABLES.md`).
2. Start services:
   ```bash
   docker compose -f docker-compose.prod.yml up -d --build
   ```
3. Validate:
   ```bash
   curl http://localhost/healthz
   curl http://localhost/api/v1/readyz
   ```
4. Run DB migrations:
   ```bash
   docker compose -f docker-compose.prod.yml exec backend flask db upgrade
   ```

## Notes

- Keep secrets outside git.
- Prefer pinned image tags for stricter release control.
- Enable TLS by terminating HTTPS before/at Nginx according to your existing infrastructure.
