# Database Migrations (Flask-Migrate / Alembic)

This repository uses **Flask-Migrate** (Alembic under the hood) for schema migrations.

## Initialize locally (one-time)
If migrations are not initialized yet in your local checkout:

```bash
cd backend
flask db init
```

## Create a migration

```bash
cd backend
flask db migrate -m "message"
```

## Apply migrations

```bash
cd backend
flask db upgrade
```

## Review before commit
1. Open generated migration files and verify table/column changes.
2. Check downgrade correctness.
3. Run tests after `flask db upgrade`.

Migrations must always be reviewed before production deploys to avoid destructive/incorrect schema drift.

## Critical model groups to track
- User
- Session
- ApiKey
- Plan
- FeatureLimit
- DailyUsage
- PaymentTransaction
- PromoCode
- AuditEvent
- Asset / Market / Analysis / Decision / Risk models (if present)
