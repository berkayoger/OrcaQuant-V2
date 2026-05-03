# Risk Engine

Risk motoru tarihsel oynaklık, gerileme ve Monte Carlo aşağı yön metriklerini birleştirerek 0-100 risk skoru üretir.

- Girdi: OHLCV satırları + MonteCarloResult.
- Çıktı: risk_score, risk_level, alt risk bileşenleri, stop-loss yüzdesi önerisi, gerekçeler ve uyarılar.
- Kısıtlar: Model tek başına karar verdirmez; portföy/likidite/kişisel hedefler kapsam dışıdır.
- Bu sonuçlar karar destekli senaryo değerlendirmesidir, kesin tahmin değildir.
- Not financial advice.
