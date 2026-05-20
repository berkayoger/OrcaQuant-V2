# Project Structure
- `backend/app/api`: thin HTTP routes.
- `backend/app/services`: business logic (no Flask request dependency).
- `backend/app/repositories`: persistence only (no policy).
- `backend/app/core/security`: reusable guards/security utilities.
- `backend/tests`: sqlite/in-memory test suite.
- `frontend/src/features`: feature modules.
- `frontend/src/shared`: shared API/auth/storage primitives.
