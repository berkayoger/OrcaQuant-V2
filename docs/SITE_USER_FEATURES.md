# Site User Features

This document tracks the normal site-user capabilities implemented in the V2 backend.

## User home

Endpoint: `GET /api/v1/me/home`

Returns a customer-facing summary for dashboard hydration:

- user identity and plan status
- profile snapshot
- watchlist count
- alert count and active-alert count
- unread notification count
- onboarding checklist
- quick actions

## Profile and onboarding

Endpoints:

- `GET /api/v1/profile/`
- `PATCH /api/v1/profile/`
- `POST /api/v1/profile/onboarding`

Supported profile fields:

- `display_name`
- `bio`
- `avatar_url`
- `risk_profile`: `CONSERVATIVE`, `BALANCED`, `AGGRESSIVE`
- `preferred_horizon_days`
- `max_drawdown_tolerance`
- `capital`
- `preferred_currency`
- `locale`
- `timezone`
- `theme`

## Settings

Endpoints:

- `GET /api/v1/settings/`
- `PATCH /api/v1/settings/`
- `GET /api/v1/settings/notifications`
- `PATCH /api/v1/settings/notifications`
- `GET /api/v1/settings/privacy`
- `PATCH /api/v1/settings/privacy`

Supported settings:

- locale
- timezone
- theme: `light`, `dark`, `system`
- preferred currency: `TRY`, `USD`, `EUR`, `USDT`
- notification preferences
- privacy preferences

## Account data export

Endpoint: `GET /api/v1/me/export`

Exports user-owned account data for self-service portability:

- account basics
- profile/settings snapshot
- watchlist symbols
- alert rules
- recent notifications
- session list metadata

Sensitive fields such as password hashes and refresh token hashes are intentionally excluded.

## Sessions and security

Endpoints:

- `GET /api/v1/me/sessions`
- `DELETE /api/v1/me/sessions/{session_id}`
- `DELETE /api/v1/me/sessions`
- `PATCH /api/v1/me/password`
- `POST /api/v1/me/deactivate`

Security behavior:

- Users can list their active and historical sessions.
- Users can revoke one session or all sessions.
- Password change requires the current password, updates the password hash, increments token version, and revokes refresh sessions.
- Account deactivation requires the current password, disables the user, increments token version, and revokes refresh sessions.

## Remaining provider work

These backend contracts are ready for frontend binding. The remaining work is integration-level, not core modeling:

- connect real email/SMS verification provider
- build frontend screens for profile/settings/security/export
- add optional audit emails for sensitive actions
