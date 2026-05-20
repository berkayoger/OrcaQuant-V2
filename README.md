# OrcaQuant V2

OrcaQuant V2 is a layered Flask + React skeleton with authenticated analysis endpoints, plan-based usage limits, and disabled-by-default billing.

## Current implemented scope
- Auth: register/login/refresh/logout with JWT access+refresh and session-backed refresh validation.
- Plans/usage: `seed-plans` CLI, per-feature daily quotas, protected analysis endpoints.
- User self endpoints: `/api/v1/me/`, `/api/v1/me/usage`.
- Billing skeleton: safe 501 behavior when disabled or not implemented.

## Quick start
1. Copy env: `cp .env.example .env`.
2. Run stack: `docker compose up --build`.
3. Seed plans in backend container: `flask seed-plans`.
4. Run tests: `pytest backend/tests`.

## Migration note
Database migrations must be reviewed before production deploy. See `backend/migrations/README.md`.
