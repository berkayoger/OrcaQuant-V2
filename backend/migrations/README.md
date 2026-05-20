# Backend Alembic Migrations

Use Flask-Migrate/Alembic.

- Create: `flask db migrate -m "message"`
- Apply: `flask db upgrade`
- Review generated operations before commit and production rollout.
