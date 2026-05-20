# Database Schema (Current)
Core models in use:
- `User`, `Session`, `ApiKey`
- `Plan`, `FeatureLimit`, `DailyUsage`
- `PaymentTransaction`, `PromoCode`, `AuditEvent`
- Analysis domain models already present in `backend/app/models/*`.

Use migrations for persistent DB changes; do not rely on `create_all` outside tests.
