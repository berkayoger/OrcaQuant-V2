# Local Development
- Copy `.env.example` to `.env` and set non-secret local values.
- Start services: `docker compose up --build`.
- Backend shell: `docker compose exec backend bash`.
- Run plan seed: `flask seed-plans`.
- Run backend tests (SQLite in-memory): `pytest backend/tests`.
- Run frontend build locally: `cd frontend && npm install && npm run build`.
