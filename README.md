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
