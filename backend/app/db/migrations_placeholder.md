# Database migrations

This project uses **Flask-Migrate/Alembic** under `backend/migrations`.

## Initialize (already committed)
- Alembic environment: `backend/migrations/env.py`
- Revision scripts: `backend/migrations/versions/`
- Initial committed revision: `20260520_000001_initial_schema.py`

## Local workflow
From `backend/`:

```bash
export FLASK_APP=app.wsgi:app
flask db upgrade
flask db migrate -m "describe change"
flask db upgrade
```

## Production requirement
Do **not** use `db.create_all()` for production schema management.
Always apply Alembic migrations (`flask db upgrade`) during deployment.

## Notes
- Test fixtures may still use `db.create_all()` for isolated in-memory test setup.
- `daily_usage` integrity is enforced with a unique key:
  `(user_id, feature_key, usage_date)`.
