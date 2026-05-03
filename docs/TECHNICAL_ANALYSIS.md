# Technical Analysis (Sprint 5)

Bu sprintte ilk çalışan analiz akışı devreye alınmıştır:
OHLCV verisi -> teknik gösterge hesaplaması -> teknik skor üretimi -> veritabanına kayıt -> API yanıtı.

## Uygulanan Göstergeler

- SMA 20
- SMA 50
- EMA 12
- EMA 26
- RSI 14
- MACD (line, signal, histogram)
- Bollinger Bands (20, 2 std)
- ATR 14
- Volume Ratio (son hacim / 20 periyot ortalaması)

## Skorlama Yaklaşımı

Motor 0-100 arası alt skorlar üretir:

- trend_score
- momentum_score
- volatility_score
- volume_score

Toplam teknik `signal_score`, alt skorların ağırlıklı birleşimidir.
Karar etiketi (decision_hint):

- `ACCUMULATE`: 75+
- `WATCH`: 40-74 arası
- `AVOID`: 40 altı

Etiketler yalnızca teknik sinyal özeti verir; kesin yatırım tavsiyesi değildir.

## Sınırlamalar

- Hesaplama geçmiş veriye dayanır; gelecek performansı garanti etmez.
- Göstergeler tek başına yeterli değildir; temel analiz, haber akışı ve risk profili ayrı değerlendirilmelidir.
- Şimdilik yalnızca örnek sağlayıcıdan gelen deterministik piyasa verisi kullanılmaktadır.

## Neden Bu Sprintte Monte Carlo Yok?

Sprint 5 hedefi veri hattını sağlamlaştırmak ve teknik analiz dikeyini uçtan uca çalıştırmaktır.
Monte Carlo, portföy optimizasyonu ve nihai yatırım tavsiyesi; daha fazla modelleme, doğrulama ve açıklanabilirlik gerektirdiği için sonraki sprintlere bırakılmıştır.

## Not

Bu modül **yatırım tavsiyesi değildir**. Çıktılar araştırma ve izleme amacıyla teknik sinyal özetidir.
