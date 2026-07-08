# OrcaQuant Product Feature Suite

This document tracks the customer-facing feature contracts added after the Market Cockpit and Alert Rule Engine MVP.

## Added feature contracts

- **Orca Daily Brief**: Daily market summary generated from Market Cockpit signals.
- **Asset Detail**: Per-symbol detail contract with technical snapshot, risk/advantage explanations, alert suggestions, and quick actions.
- **Orca Radar v2**: Radar variants for daily top assets, momentum, risk, volume, trend, reversal watch, breakout watch, and pump-risk watch.
- **Portfolio Assistant**: Portfolio risk explanation based on allocation, asset risk score, opportunity score, concentration, and portfolio-level alert suggestions.
- **Plan Entitlements**: Free / Pro / Premium feature and limit contracts.
- **Admin Product Analytics**: Alert rule usage, enabled/disabled counts, trigger counts, metric distribution, and top watched symbols.

## Important boundaries

- The system remains decision support and does not provide investment advice.
- Alert evaluation produces events, but notification delivery workers are a separate implementation step.
- Radar v2 currently uses technical/price/volume cockpit signals. Whale, funding, open-interest, social hype, and news sentiment inputs are planned provider integrations.
- Backtest reporting is represented as a product contract boundary until historical signal outcome tracking is added.

## Public API contracts

- `GET /api/v1/dashboard/daily-brief`
- `GET /api/v1/dashboard/assets/<symbol>`
- `GET /api/v1/dashboard/radar/variants`
- `POST /api/v1/dashboard/portfolio/assistant`
- `GET /api/v1/dashboard/plans`
- `GET /api/v1/dashboard/admin/analytics`
- `GET /api/v1/dashboard/features/suite`
