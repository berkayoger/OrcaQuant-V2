# OrcaQuant v2 — Proje Yapısı Planı

Bu doküman, hedef dosya ağacını ve önerilen oluşturma sırasını baz alır.

## Öncelikli oluşturma sırası

### 1) Repo iskeleti
- README.md
- .env.example
- .gitignore
- .editorconfig
- .dockerignore
- docker-compose.yml
- backend/
- frontend/
- infra/
- docs/
- scripts/
- .github/

### 2) Backend çekirdeği
- `backend/app/__init__.py`
- `backend/app/config.py`
- `backend/app/extensions.py`
- `backend/app/factory.py`
- `backend/app/wsgi.py`
- `backend/app/api/v1/health_routes.py`
- `backend/app/core/errors/exceptions.py`
- `backend/app/core/errors/handlers.py`
- `backend/app/core/security/security_headers.py`
- `backend/app/core/observability/logger.py`
- `backend/app/core/observability/health_checks.py`

### 3) Frontend çekirdeği
- `frontend/src/main.tsx`
- `frontend/src/app/App.tsx`
- `frontend/src/app/router.tsx`
- `frontend/src/app/providers.tsx`
- `frontend/src/shared/lib/apiClient.ts`
- `frontend/src/pages/public/HomePage.tsx`
- `frontend/src/pages/auth/LoginPage.tsx`
- `frontend/src/pages/auth/RegisterPage.tsx`
- `frontend/src/pages/app/DashboardPage.tsx`

## Not

İlk sprintte boş dosya + temel import düzeni yeterlidir. İçerik sprint bazlı doldurulmalıdır.
