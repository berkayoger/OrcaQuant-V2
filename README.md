# OrcaQuant v2

Bu depo, OrcaQuant v2 için katmanlı SaaS mimarisi iskeletini içerir.

## Mimari prensipleri

- **Route iş mantığı yazmaz.**
- **Service HTTP bilmez.**
- **Engine DB bilmez.**
- **Repository karar vermez.**
- **Security guard kritik akışlarda zorunludur.**

## İlk kurulum hedefi

Bu aşamada tüm sistemin detay implementasyonu değil, proje iskeleti ve çekirdek dosya ayrımı hedeflenir.

1. Repo omurgası (`backend`, `frontend`, `infra`, `docs`, `scripts`, `.github`)
2. Backend çekirdeği
3. Frontend çekirdeği
4. Güvenlik, faturalama ve engine katmanlarına kademeli geçiş

Ayrıntılı kapsam için `docs/PROJECT_STRUCTURE.md` dosyasına bakın.

## V2 migration skeleton

Bu sprintte, V1 yeteneklerinin V2'ye kademeli taşınması için import-safe iskelet modüller eklendi:

- Backend'te `auth`, `users`, `plans`, `usage`, `analysis`, `decision`, `llm`, `payments`, `realtime`, `cache`, `audit`, `db`, `common` modülleri.
- Frontend'te feature-bazlı sayfa/API/type iskeletleri.
- Migration planı ve modül eşleşmeleri için yeni roadmap dokümantasyonu.
