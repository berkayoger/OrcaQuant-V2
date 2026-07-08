# OrcaQuant-V2

## Local quickstart
- `docker compose up --build`
- Copy env: `cp .env.example .env` (create values locally, never commit secrets).
- Backend tests: `cd backend && pytest`
- Frontend build: `cd frontend && npm run build`
- Seed plans: `cd backend && flask seed-plans`

## Current V2 posture
- Implemented: auth/register/login/refresh/logout with hashed refresh-session storage and refresh-token rotation/reuse detection.
- Implemented: usage guard for plan/feature limits and technical analysis routes, plus scenario-risk/full analysis skeleton routes.
- Implemented: lightweight OpenAPI JSON docs at `/api/v1/docs/openapi.json` and docs status at `/api/v1/docs/`.
- Implemented: billing provider boundary with fake/dev provider, Iyzico adapter slot, readiness reporting, callback event persistence, idempotent initiation, and production config guardrails.
- Not implemented yet: real outbound payment provider SDK/API call, realtime streaming transport, full admin CRUD surface, production market-data provider integration, optional OpenAPI UI.


## Deployment docs
- Production deployment: `docs/PRODUCTION_DEPLOYMENT.md`
- Environment variables: `docs/ENVIRONMENT_VARIABLES.md`
- External dependency binding plan: `docs/EXTERNAL_DEPENDENCIES.md`
- Backup/restore: `docs/BACKUP_RESTORE.md`
