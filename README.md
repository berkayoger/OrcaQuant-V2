# OrcaQuant-V2

## Local quickstart
- `docker compose up --build`
- Copy env: `cp .env.example .env` (create values locally, never commit secrets).
- Backend tests: `cd backend && pytest`
- Frontend build: `cd frontend && npm run build`
- Seed plans: `cd backend && flask seed-plans`

## Current module posture
- Auth/register/login/refresh/logout implemented with hashed refresh-session storage.
- Refresh token rotation and reuse detection are implemented (rotating refresh contract is active).
- Usage guard enforces plan + feature limits on protected analysis routes.
- Billing is disabled by default and returns placeholder `501` when enabled.
- Realtime is disabled by default and only exposes status endpoint.
