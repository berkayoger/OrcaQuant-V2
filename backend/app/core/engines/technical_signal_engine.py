from __future__ import annotations

import pandas as pd

from app.core.engines.enums import Decision
from app.core.engines.schemas import TechnicalIndicatorSnapshot, TechnicalSignalResult
from app.core.errors.exceptions import ValidationError


class TechnicalSignalEngine:
    def run(self, ohlcv_rows: list[dict]) -> TechnicalSignalResult:
        if len(ohlcv_rows) < 50:
            raise ValidationError("Technical analysis için en az 50 OHLCV satırı gerekir")

        df = pd.DataFrame(ohlcv_rows)
        required_cols = {"timestamp", "open", "high", "low", "close", "volume"}
        if not required_cols.issubset(df.columns):
            raise ValidationError("OHLCV verisi gerekli alanları içermiyor")

        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df = df.sort_values("timestamp").reset_index(drop=True)

        close = df["close"].astype(float)
        high = df["high"].astype(float)
        low = df["low"].astype(float)
        volume = df["volume"].astype(float)

        sma_20 = close.rolling(20).mean()
        sma_50 = close.rolling(50).mean()
        ema_12 = close.ewm(span=12, adjust=False).mean()
        ema_26 = close.ewm(span=26, adjust=False).mean()

        delta = close.diff()
        gains = delta.clip(lower=0)
        losses = (-delta).clip(lower=0)
        avg_gain = gains.rolling(14).mean()
        avg_loss = losses.rolling(14).mean()
        rs = avg_gain / avg_loss.replace(0, 1e-9)
        rsi_14 = 100 - (100 / (1 + rs))

        macd = ema_12 - ema_26
        macd_signal = macd.ewm(span=9, adjust=False).mean()
        macd_histogram = macd - macd_signal

        bollinger_middle = sma_20
        rolling_std = close.rolling(20).std()
        bollinger_upper = bollinger_middle + (2 * rolling_std)
        bollinger_lower = bollinger_middle - (2 * rolling_std)

        prev_close = close.shift(1)
        true_range = pd.concat(
            [(high - low), (high - prev_close).abs(), (low - prev_close).abs()], axis=1
        ).max(axis=1)
        atr_14 = true_range.rolling(14).mean()

        volume_ratio_series = volume / volume.rolling(20).mean()

        latest_close = float(close.iloc[-1])
        latest_sma20 = self._to_float(sma_20.iloc[-1])
        latest_sma50 = self._to_float(sma_50.iloc[-1])
        latest_rsi = self._to_float(rsi_14.iloc[-1])
        latest_macd = self._to_float(macd.iloc[-1])
        latest_macd_signal = self._to_float(macd_signal.iloc[-1])
        latest_macd_hist = self._to_float(macd_histogram.iloc[-1])
        latest_atr = self._to_float(atr_14.iloc[-1])
        latest_volume_ratio = self._to_float(volume_ratio_series.iloc[-1])

        trend_score = 0.0
        trend_score += 60.0 if latest_sma50 and latest_close >= latest_sma50 else 25.0
        trend_score += 40.0 if latest_sma20 and latest_close >= latest_sma20 else 15.0
        trend_score = min(100.0, trend_score)

        momentum_score = 50.0
        if latest_rsi is not None:
            momentum_score = max(0.0, 100.0 - (abs(50.0 - latest_rsi) * 2.0))
        if latest_macd is not None and latest_macd_signal is not None:
            momentum_score = min(100.0, momentum_score + (15.0 if latest_macd >= latest_macd_signal else -15.0))

        volatility_score = 50.0
        atr_ratio = (latest_atr / latest_close) if latest_atr else 0.0
        volatility_score = max(0.0, min(100.0, 100.0 - (atr_ratio * 700.0)))

        volume_score = 50.0
        if latest_volume_ratio is not None:
            volume_score = max(0.0, min(100.0, latest_volume_ratio * 50.0))

        signal_score = round((trend_score * 0.35) + (momentum_score * 0.30) + (volatility_score * 0.20) + (volume_score * 0.15), 2)

        decision_hint = Decision.WATCH
        if signal_score >= 75:
            decision_hint = Decision.ACCUMULATE
        elif signal_score < 40:
            decision_hint = Decision.AVOID

        direction = "flat"
        if latest_sma20 and latest_sma50:
            if latest_close > latest_sma20 > latest_sma50:
                direction = "uptrend"
            elif latest_close < latest_sma20 < latest_sma50:
                direction = "downtrend"

        flags: list[str] = []
        reasons: list[str] = []
        if latest_rsi is not None and latest_rsi >= 70:
            flags.append("overbought_rsi")
            reasons.append("RSI 70 üstünde, kısa vadede aşırı alım riski var.")
        if latest_rsi is not None and latest_rsi <= 30:
            flags.append("oversold_rsi")
            reasons.append("RSI 30 altında, varlık aşırı satım bölgesinde.")
        if atr_ratio >= 0.08:
            flags.append("high_volatility")
            reasons.append("ATR/close oranı yüksek, oynaklık artmış durumda.")
        if latest_volume_ratio is not None and latest_volume_ratio >= 2:
            flags.append("unusual_volume")
            reasons.append("Son hacim 20 periyot ortalamasının oldukça üzerinde.")
        if latest_sma50 and latest_close < latest_sma50:
            flags.append("weak_trend")
            reasons.append("Fiyat SMA50 altında, trend zayıf görünüyor.")
        if not reasons:
            reasons.append("Teknik göstergeler nötr dengede, net bir uç sinyal bulunmuyor.")

        indicators = TechnicalIndicatorSnapshot(
            close=latest_close,
            sma_20=latest_sma20,
            sma_50=latest_sma50,
            ema_12=self._to_float(ema_12.iloc[-1]),
            ema_26=self._to_float(ema_26.iloc[-1]),
            rsi_14=latest_rsi,
            macd=latest_macd,
            macd_signal=latest_macd_signal,
            macd_histogram=latest_macd_hist,
            bollinger_upper=self._to_float(bollinger_upper.iloc[-1]),
            bollinger_middle=self._to_float(bollinger_middle.iloc[-1]),
            bollinger_lower=self._to_float(bollinger_lower.iloc[-1]),
            atr_14=latest_atr,
            volume_ratio=latest_volume_ratio,
        )

        return TechnicalSignalResult(
            signal_score=signal_score,
            trend_score=round(trend_score, 2),
            momentum_score=round(momentum_score, 2),
            volatility_score=round(volatility_score, 2),
            volume_score=round(volume_score, 2),
            decision_hint=decision_hint,
            direction=direction,
            indicators=indicators,
            flags=flags,
            reasons=reasons,
        )

    @staticmethod
    def _to_float(value: float | None) -> float | None:
        if value is None or pd.isna(value):
            return None
        return float(value)
