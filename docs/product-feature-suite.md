# OrcaQuant Product Feature Suite

This document tracks the customer-facing feature contracts added after the Market Cockpit and Alert Rule Engine MVP.

## Added feature contracts

- **Orca Daily Brief**: Daily market summary generated from Market Cockpit signals.
- **Asset Detail**: Per-symbol detail contract with technical snapshot, risk/advantage explanations, alert suggestions, and quick actions.
- **Orca Radar v2**: Radar variants for daily top assets, momentum, risk, volume, trend, reversal watch, breakout watch, and pump-risk watch.
- **Portfolio Assistant**: Portfolio risk explanation based on allocation, asset risk score, opportunity score, concentration, and portfolio-level alert suggestions.
- **Plan Entitlements**: Free / Pro / Premium feature and limit contracts.
- **Admin Product Analytics**: Alert rule usage, enabled/disabled counts, trigger counts, metric distribution, and top watched symbols.
- **Notification Center**: Persisted in-app notifications for triggered alerts and daily briefs.

## Production-ready layer

- Alert evaluation now persists triggered events as `notifications` rows.
- Notification deduplication uses `source_event_key`, so the same alert event or same daily brief is not inserted repeatedly.
- In-app delivery is implemented immediately; email, Telegram, SMS, and push are represented as `not_configured` until real providers are wired through environment-backed adapters.
- Daily Brief can now be saved as a notification through the notification center API.
- Admins can run an authenticated alert delivery pass with `POST /api/v1/alerts/evaluate-all`; this can later be called by Celery or a scheduled job.

## Important boundaries

- The system remains decision support and does not provide investment advice.
- Radar v2 currently uses technical/price/volume cockpit signals. Whale, funding, open-interest, social hype, and news sentiment inputs are planned provider integrations.
- Backtest reporting is represented as a product contract boundary until historical signal outcome tracking is added.
- Production database deployments need the new `notifications` table available before enabling delivery routes.

## Public API contracts

- `GET /api/v1/dashboard/daily-brief`
- `GET /api/v1/dashboard/assets/<symbol>`
- `GET /api/v1/dashboard/radar/variants`
- `POST /api/v1/dashboard/portfolio/assistant`
- `GET /api/v1/dashboard/plans`
- `GET /api/v1/dashboard/admin/analytics`
- `GET /api/v1/dashboard/features/suite`
- `POST /api/v1/alerts/evaluate-all`
- `GET /api/v1/notifications`
- `POST /api/v1/notifications/daily-brief`
- `PATCH /api/v1/notifications/<notification_id>/read`
- `PATCH /api/v1/notifications/read-all`
- `DELETE /api/v1/notifications/<notification_id>`
