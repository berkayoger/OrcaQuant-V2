# Local Development

## Docker Compose
```bash
docker compose up --build
```

## Environment
Create `.env` from local values (no real secrets):
- `SECRET_KEY`
- `DATABASE_URL`
- `JWT_ACCESS_TOKEN_MINUTES`
- `JWT_REFRESH_TOKEN_DAYS`
- `ENABLE_BILLING=false`
- `ENABLE_REALTIME=false`

## Commands
- Backend tests: `cd backend && pytest`
- Frontend build: `cd frontend && npm ci && npm run build`
- Plan seed: `cd backend && flask seed-plans`
