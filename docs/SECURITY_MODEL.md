# Security Model
- Layered guards: auth, usage, admin/permission guards.
- JWT access/refresh separation with typed token payloads.
- Refresh session revocation supported via logout.
- Usage guard fails closed for protected features.
- Billing callback must not mutate subscription without provider verification.
