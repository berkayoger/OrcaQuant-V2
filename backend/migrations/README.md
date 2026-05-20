# Backend Migrations
Run from `backend/`.

## Initialize locally (one-time)
- `flask db init`

## Create migration
- `flask db migrate -m "describe change"`

## Apply migration
- `flask db upgrade`

## Models that must be tracked
At minimum:
- User, Session, ApiKey
- Plan, FeatureLimit, DailyUsage
- PaymentTransaction, PromoCode, AuditEvent
- Existing analysis/decision/risk/asset/market models in `app/models`.

## Production warning
Always review generated migration scripts before deploy; auto-generated diffs can be unsafe.
