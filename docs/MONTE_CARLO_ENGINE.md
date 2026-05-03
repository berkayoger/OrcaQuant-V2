# Monte Carlo Engine

Bu modül OHLCV kapanış verilerinden log getiri dağılımı çıkararak olasılıksal senaryo simülasyonu üretir.

- Girdi: OHLCV satırları, ufuk gün sayısı, hedef listesi.
- Çıktı: terminal fiyat/getiri yüzdelikleri, hedef dokunma ve terminal olasılıkları, VaR/CVaR ve belirsizlik skoru.
- Kısıtlar: Geçmiş dağılım varsayımı geleceği birebir temsil etmez; dış haber akışını modellemez.
- Bu sonuçlar senaryo analizi içindir, kesin tahmin değildir.
- Not financial advice.
