# External Dependency Foundation

This document defines the boundary for third-party systems so OrcaQuant can be wired to real providers without leaking provider-specific logic into core product code.

## Design rule

Core routes and services must talk to a provider interface/factory. Provider-specific credentials, payload formats, signatures, SDK clients, and HTTP behavior stay inside the adapter package.

## Payment provider boundary

Current adapter package: `backend/app/payments/`

Implemented pieces:

- `PaymentProvider` protocol for provider initiation and callback verification.
- `ProviderInitiateRequest` includes transaction, user, plan, amount, currency, customer email, return URLs, callback URL, and metadata.
- `ProviderInitiateResponse` normalizes provider payment id, conversation id, checkout URL, and raw payload.
- `ProviderVerificationResult` normalizes callback verification, mapped payment status, provider ids, raw payload, and failure reason.
- `ProviderReadiness` exposes provider configuration status to `/api/v1/billing/status` and `/api/v1/billing/providers`.
- `fake` provider remains development-only.
- `iyzico` provider has the adapter slot ready; the real SDK/API call and cryptographic verification should be implemented inside `iyzico_provider.py` only.

### Runtime guardrails

- `ENABLE_BILLING=false` disables billing routes that mutate state.
- `BILLING_PROVIDER=fake` is blocked in production when billing is enabled.
- `BILLING_PROVIDER=iyzico` requires `IYZICO_API_KEY`, `IYZICO_SECRET`, and `IYZICO_BASE_URL` in production.
- Checkout success/failure URLs and callback URL must be valid `http(s)` URLs.
- Callback processing records `PaymentEvent` rows for idempotent webhook handling.

### Binding Iyzico later

Only the adapter should need provider-specific code:

1. Install/choose the Iyzico SDK or thin HTTP client.
2. Replace the skeleton payload in `IyzicoProvider.initiate_payment` with the real checkout-session call.
3. Replace the mocked verification boundary in `IyzicoProvider.verify_callback` with the real signature/HMAC verification.
4. Keep route responses unchanged so frontend/admin contracts do not move.
5. Keep `ProviderReadiness` reporting missing credentials and mode.

## Other external systems

The same pattern should be used for the next dependencies:

- Market data providers: keep provider SDK/API logic behind the existing market-data provider setting.
- Notification providers: keep email, Telegram, push, and SMS senders behind channel adapters; in-app notification persistence remains the source of truth.
- News/social sentiment: add a provider registry before wiring external APIs.

Hard rule: no route should directly import a third-party SDK. Routes call services; services call provider interfaces; adapters talk to vendors.
