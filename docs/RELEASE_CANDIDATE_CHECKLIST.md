# Release Candidate Checklist (V2)

## Required Production Environment Variables
- `FLASK_ENV=production`
- `SECRET_KEY` (strong, non-default)
- `DATABASE_URL`
- `REDIS_URL`
- `RATE_LIMIT_STORAGE_URI`
- `CORS_ALLOWED_ORIGINS` (explicit allowlist)
- `JWT_ACCESS_TOKEN_MINUTES`
- `JWT_REFRESH_TOKEN_DAYS`
- `ENABLE_BILLING`
- `ENABLE_REALTIME`
- If billing enabled: `IYZICO_API_KEY`, `IYZICO_SECRET`, `IYZICO_BASE_URL`

## Validation Commands
- Backend tests: `cd backend && pytest -q`
- Frontend checks: `cd frontend && npm ci && npm run typecheck && npm run build`
- Compose validation:
  - `docker compose config`
  - `docker compose -f docker-compose.prod.yml config`

## Database and Seed
- Run migrations: `cd backend && flask db upgrade`
- Seed plans: `cd backend && flask seed-plans`

## Health / Readiness
- App health: `GET /api/v1/healthz`
- App readiness: `GET /api/v1/readyz`
- Limits status smoke: `GET /api/v1/limits/status` (authenticated)

## Rollback Notes
- Keep previous image tags for backend/nginx.
- Roll back application containers first, then rerun `flask db upgrade` only if target revision expects newer schema.
- If migration introduced incompatible schema changes, restore DB backup/snapshot before traffic cutover.

## Known Not-Yet-Production-Ready Areas
- Real billing provider verification beyond mock/sandbox confidence.
- Full realtime streaming infrastructure hardening.
- Production-grade market data provider coverage and failover.
- Admin UI completeness and operational tooling depth.
