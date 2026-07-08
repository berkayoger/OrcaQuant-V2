# Account Lifecycle

This document defines the account flows implemented in V2 and the provider boundary for verification-code delivery.

## Implemented flows

### Registration

Endpoint: `POST /api/v1/auth/register`

- Creates a user with email and password.
- Accepts an optional `username`.
- Reserves the username forever if supplied and available.
- Sends an `email_verification` code after registration.
- Returns access/refresh tokens so the user can continue onboarding.

### Email verification

Endpoints:

- `POST /api/v1/auth/verification-code/send` with `purpose=email_verification`
- `POST /api/v1/auth/email/verify`

Verification codes are hashed at rest, expire after `ACCOUNT_VERIFICATION_CODE_TTL_MINUTES`, and lock after `ACCOUNT_VERIFICATION_MAX_ATTEMPTS` failed attempts.

### Code-based login

Endpoints:

- `POST /api/v1/auth/login/code/send`
- `POST /api/v1/auth/login/code`

The verify endpoint consumes the login code and issues normal access/refresh tokens.

### Forgot/reset password

Endpoints:

- `POST /api/v1/auth/password/forgot`
- `POST /api/v1/auth/password/reset`

Forgot-password responses avoid account enumeration by returning `sent_if_account_exists`. Reset consumes a password-reset code, updates the password hash, increments the user token version, and revokes refresh sessions.

### Username availability and changes

Endpoints:

- `GET /api/v1/auth/username/check?username=...` for public signup checks.
- `GET /api/v1/me/username/check?username=...` for authenticated checks.
- `PATCH /api/v1/me/username` for authenticated changes.

Username rules:

- Lowercase normalization.
- 3-24 characters.
- Allowed characters: letters, numbers, dot, underscore.
- Cannot start/end with dot or underscore.
- Repeated/mixed punctuation such as `..`, `__`, `._`, `_.` is rejected.
- Reserved words such as `admin`, `api`, `support`, and `orcaquant` are blocked.
- Once a username is claimed, it is stored in `UsernameReservation` and cannot be reused after a change.

## Delivery provider boundary

Current delivery service: `backend/app/services/account/verification_delivery_service.py`

The app currently supports a safe development/test delivery boundary:

- In test/debug mode, the raw code may be returned as `debug_code`.
- In production, `ACCOUNT_CODE_DEBUG_RESPONSE=true` is blocked.
- A real email/SMS provider should be wired only inside `VerificationDeliveryService` or a future adapter registry.

Hard rule: routes should not import email/SMS provider SDKs directly.
