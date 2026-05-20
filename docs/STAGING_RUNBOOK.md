# Staging Runbook

## 1) Prepare Environment
1. Copy env template:
   - `cp .env.example .env`
2. Edit `.env` with staging-safe values (no production secrets).

## 2) Start Stack
- `docker compose up -d --build`
- Check running services: `docker compose ps`

## 3) Run Migrations
- `docker compose exec backend flask db upgrade`

## 4) Seed Plan Data
- `docker compose exec backend flask seed-plans`

## 5) Health and Readiness Checks
- `curl http://localhost:5000/api/v1/healthz`
- `curl http://localhost:5000/api/v1/readyz`

## 6) Smoke Auth Flow
1. Register:
   - `curl -X POST http://localhost:5000/api/v1/auth/register -H 'Content-Type: application/json' -d '{"email":"staging-user@example.com","password":"Password123"}'`
2. Login:
   - `curl -X POST http://localhost:5000/api/v1/auth/login -H 'Content-Type: application/json' -d '{"email":"staging-user@example.com","password":"Password123"}'`
3. Save `access_token` from response.

## 7) Limits Status Smoke Test
- `curl http://localhost:5000/api/v1/limits/status -H 'Authorization: Bearer <ACCESS_TOKEN>'`
- Verify payload includes `plan_id`, `plan`, and `features`.

## 8) Inspect Logs
- All services: `docker compose logs -f --tail=200`
- Backend only: `docker compose logs -f --tail=200 backend`

## 9) Stop / Roll Back
- Stop current stack: `docker compose down`
- Stop and clear volumes (destructive): `docker compose down -v`
- Roll back to prior image tags and restart with `docker compose up -d`.
