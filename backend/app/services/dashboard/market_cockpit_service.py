from __future__ import annotations

from dataclasses import dataclass
from statistics import mean

from app.core.engines.technical_signal_engine import TechnicalSignalEngine
from app.services.market_data.exceptions import MarketDataProviderError
from app.services.market_data.provider_factory import get_market_data_provider
from app.services.market_data.provider_protocol import OhlcvProviderProtocol
from app.services.market_data.sample_provider import SampleMarketDataProvider


@dataclass(frozen=True)
class CockpitAssetSeed:
    symbol: str
    name: str
    theme: str


class MarketCockpitService:
    """Builds the product-facing Market Cockpit contract.

    The cockpit now tries the configured live provider first and falls back to
    deterministic sample data when the provider is unavailable. This keeps the
    dashboard usable in local/dev environments while making the same contract
    ready for real market-data providers in production.
    """

    _DEFAULT_ASSETS = [
        CockpitAssetSeed("BTC", "Bitcoin", "Market anchor"),
        CockpitAssetSeed("ETH", "Ethereum", "Smart-contract core"),
        CockpitAssetSeed("SOL", "Solana", "High-beta momentum"),
        CockpitAssetSeed("AVAX", "Avalanche", "Layer-1 rotation"),
        CockpitAssetSeed("XRP", "XRP", "Liquidity watcher"),
    ]
    _ASSET_NAMES = {asset.symbol: asset for asset in _DEFAULT_ASSETS}
    _MAX_SYMBOLS = 15

    def __init__(self, provider: OhlcvProviderProtocol | None = None, technical_engine: TechnicalSignalEngine | None = None) -> None:
        self.provider = provider or get_market_data_provider()
        self.fallback_provider = SampleMarketDataProvider()
        self.technical_engine = technical_engine or TechnicalSignalEngine()

    def build_cockpit(self, symbols: list[str] | None = None, watchlist_symbols: list[str] | None = None) -> dict:
        seeds = self._resolve_asset_seeds(symbols)
        watchlist = self._normalize_symbols(watchlist_symbols or [])
        assets = [self._build_asset_card(asset, is_watchlisted=asset.symbol in watchlist) for asset in seeds]
        radar = sorted(assets, key=lambda item: item["opportunity_score"], reverse=True)
        avg_technical = round(mean(item["technical_score"] for item in assets), 2)
        avg_risk = round(mean(item["risk_score"] for item in assets), 2)
        avg_volume = round(mean(item["volume_score"] for item in assets), 2)
        provider_sources = sorted({asset["data_source"] for asset in assets})

        return {
            "module": "market_cockpit",
            "status": "customer_mvp_contract",
            "investment_advice": False,
            "data_source": ",".join(provider_sources),
            "provider_sources": provider_sources,
            "disclaimer": "OrcaQuant yatırım tavsiyesi vermez; riskleri, avantajları ve izlenebilir sinyalleri karar desteği olarak açıklar.",
            "market_overview": self._build_market_overview(avg_technical=avg_technical, avg_risk=avg_risk, avg_volume=avg_volume),
            "radar": [self._to_radar_item(item) for item in radar],
            "watchlist_focus": [self._to_radar_item(item) for item in radar if item["is_watchlisted"]],
            "suggested_alerts": self._suggest_alerts(radar),
            "assets": assets,
            "personas": [
                {
                    "key": "pro_analyst",
                    "title": "Analiz bilen kullanıcı",
                    "value": "Teknik, hacim, risk ve fırsat sinyallerini tek kokpitte görür; sekme cambazlığı azalır.",
                },
                {
                    "key": "new_investor",
                    "title": "Analiz bilmeyen yatırımcı",
                    "value": "RSI, trend ve oynaklık gibi sinyalleri sade risk/avantaj dilinde okur.",
                },
                {
                    "key": "opportunity_hunter",
                    "title": "Fırsat arayan ama yorulan kullanıcı",
                    "value": "Orca Radar, izlenebilir varlıkları ve alarm önerilerini öne çıkarır.",
                },
            ],
        }

    def build_radar(self, symbols: list[str] | None = None) -> dict:
        cockpit = self.build_cockpit(symbols=symbols)
        return {
            "module": "orca_radar",
            "status": "customer_mvp_contract",
            "investment_advice": False,
            "items": cockpit["radar"],
            "suggested_alerts": cockpit["suggested_alerts"],
        }

    def _build_asset_card(self, seed: CockpitAssetSeed, is_watchlisted: bool = False) -> dict:
        rows, data_source = self._load_ohlcv(seed.symbol)
        technical = self.technical_engine.run(rows).to_dict()
        latest = rows[-1]
        previous = rows[-2]
        close = float(latest["close"])
        prev_close = float(previous["close"])
        change_pct = round(((close - prev_close) / prev_close) * 100, 2) if prev_close else 0.0
        volume_score = float(technical["volume_score"])
        technical_score = float(technical["signal_score"])
        risk_score = self._risk_score(technical)
        opportunity_score = self._opportunity_score(technical_score, volume_score, risk_score)
        signals = self._signals(technical, change_pct, opportunity_score, risk_score)

        return {
            "symbol": seed.symbol,
            "name": seed.name,
            "theme": seed.theme,
            "price": round(close, 4),
            "change_24h_pct": change_pct,
            "technical_score": technical_score,
            "volume_score": round(volume_score, 2),
            "risk_score": risk_score,
            "risk_level": self._risk_level(risk_score),
            "opportunity_score": opportunity_score,
            "label": self._label(opportunity_score, risk_score, technical["decision_hint"]),
            "plain_language_summary": self._summary(seed.symbol, technical, risk_score, opportunity_score),
            "advantages": self._advantages(technical, signals),
            "risks": self._risks(technical, risk_score),
            "signals": signals,
            "suggested_alerts": self._suggest_asset_alerts(seed.symbol, technical, close, opportunity_score, risk_score),
            "is_watchlisted": is_watchlisted,
            "data_source": data_source,
            "technical": technical,
        }

    def _load_ohlcv(self, symbol: str) -> tuple[list[dict], str]:
        try:
            rows = self.provider.get_ohlcv(symbol=symbol, timeframe="1d", limit=200)
            source = getattr(self.provider, "provider_name", self.provider.__class__.__name__.replace("MarketDataProvider", "").lower())
        except (MarketDataProviderError, TimeoutError, OSError, ValueError):
            rows = self.fallback_provider.get_ohlcv(symbol=symbol, timeframe="1d", limit=200)
            source = "sample_fallback"
        return rows, source

    def _resolve_asset_seeds(self, symbols: list[str] | None) -> list[CockpitAssetSeed]:
        normalized = self._normalize_symbols(symbols or [])[: self._MAX_SYMBOLS]
        if not normalized:
            return list(self._DEFAULT_ASSETS)
        return [self._ASSET_NAMES.get(symbol, CockpitAssetSeed(symbol, symbol, "Custom watch")) for symbol in normalized]

    @staticmethod
    def _normalize_symbols(symbols: list[str]) -> list[str]:
        seen: set[str] = set()
        normalized: list[str] = []
        for symbol in symbols:
            clean = "".join(ch for ch in str(symbol).upper().strip() if ch.isalnum())
            if clean and clean not in seen:
                seen.add(clean)
                normalized.append(clean)
        return normalized

    def _build_market_overview(self, avg_technical: float, avg_risk: float, avg_volume: float) -> dict:
        regime = "mixed"
        if avg_technical >= 70 and avg_risk < 55:
            regime = "risk_on"
        elif avg_risk >= 70:
            regime = "risk_off"

        return {
            "regime": regime,
            "technical_health": avg_technical,
            "risk_pressure": avg_risk,
            "volume_heat": avg_volume,
            "summary": self._market_summary(regime, avg_technical, avg_risk, avg_volume),
            "watchpoints": [
                "BTC yönü ve piyasa genel risk iştahı birlikte takip edilmeli.",
                "Hacim artışı tek başına fırsat değildir; trend ve oynaklıkla birlikte okunmalı.",
                "Yüksek fırsat skoru, düşük risk anlamına gelmez; risk seviyesi ayrı değerlendirilir.",
            ],
        }

    @staticmethod
    def _risk_score(technical: dict) -> float:
        indicators = technical.get("indicators", {})
        rsi = indicators.get("rsi_14") or 50.0
        volatility_penalty = 100.0 - float(technical.get("volatility_score", 50.0))
        rsi_pressure = max(0.0, abs(float(rsi) - 50.0) * 1.5)
        weak_trend_penalty = 18.0 if "weak_trend" in technical.get("flags", []) else 0.0
        return round(min(100.0, max(0.0, volatility_penalty + rsi_pressure + weak_trend_penalty)), 2)

    @staticmethod
    def _opportunity_score(technical_score: float, volume_score: float, risk_score: float) -> float:
        raw = (technical_score * 0.62) + (volume_score * 0.23) + ((100.0 - risk_score) * 0.15)
        return round(min(100.0, max(0.0, raw)), 2)

    @staticmethod
    def _risk_level(score: float) -> str:
        if score >= 75:
            return "high"
        if score >= 45:
            return "medium"
        return "low"

    @staticmethod
    def _label(opportunity_score: float, risk_score: float, decision_hint: str) -> str:
        if opportunity_score >= 72 and risk_score >= 65:
            return "Riskli fırsat"
        if opportunity_score >= 72:
            return "Radar lideri"
        if decision_hint == "AVOID" or risk_score >= 75:
            return "Dikkatli ol"
        if opportunity_score >= 58:
            return "İzlenebilir"
        return "Henüz erken"

    @staticmethod
    def _signals(technical: dict, change_pct: float, opportunity_score: float, risk_score: float) -> list[dict]:
        indicators = technical.get("indicators", {})
        signals: list[dict] = []
        if "unusual_volume" in technical.get("flags", []):
            signals.append({"type": "volume_spike", "label": "Hacim patlaması", "severity": "info"})
        if technical.get("direction") == "uptrend":
            signals.append({"type": "trend_continuation", "label": "Trend devamı", "severity": "positive"})
        if technical.get("direction") == "downtrend":
            signals.append({"type": "weak_trend", "label": "Zayıf trend", "severity": "warning"})
        rsi = indicators.get("rsi_14")
        if rsi is not None and rsi <= 35:
            signals.append({"type": "oversold_rebound_watch", "label": "Aşırı satıştan dönüş izlenebilir", "severity": "info"})
        if rsi is not None and rsi >= 70:
            signals.append({"type": "overbought_risk", "label": "Aşırı alım riski", "severity": "warning"})
        if change_pct >= 3 and opportunity_score >= 60:
            signals.append({"type": "momentum_burst", "label": "Momentum hızlandı", "severity": "positive"})
        if risk_score >= 70:
            signals.append({"type": "capital_protection", "label": "Sermaye koruma filtresi", "severity": "danger"})
        if not signals:
            signals.append({"type": "neutral_watch", "label": "Nötr izleme", "severity": "neutral"})
        return signals[:4]

    @staticmethod
    def _summary(symbol: str, technical: dict, risk_score: float, opportunity_score: float) -> str:
        direction = technical.get("direction", "flat")
        readable_direction = {
            "uptrend": "yukarı trend eğilimi gösteriyor",
            "downtrend": "zayıf trend bölgesinde kalıyor",
            "flat": "kararsız bölgede hareket ediyor",
        }.get(direction, "kararsız bölgede hareket ediyor")
        if opportunity_score >= 72:
            opener = f"{symbol} radarın üst sıralarında;"
        elif opportunity_score >= 58:
            opener = f"{symbol} izlenebilir bölgede;"
        else:
            opener = f"{symbol} için henüz agresif bir sinyal yok;"
        return f"{opener} teknik yapı {readable_direction}. Risk baskısı {risk_score}/100 seviyesinde; karar vermeden önce avantaj ve risk maddeleri birlikte okunmalı."

    @staticmethod
    def _advantages(technical: dict, signals: list[dict]) -> list[str]:
        advantages: list[str] = []
        indicators = technical.get("indicators", {})
        signal_types = {signal["type"] for signal in signals}
        if technical.get("direction") == "uptrend":
            advantages.append("Fiyat kısa ve orta vadeli ortalamaların üzerinde; trend yapısı destekleniyor.")
        if "volume_spike" in signal_types or float(technical.get("volume_score", 0)) >= 60:
            advantages.append("Hacim tarafında ortalamanın üzerinde ilgi var; hareketin takip edilme ihtimali artıyor.")
        if indicators.get("macd") is not None and indicators.get("macd_signal") is not None and indicators["macd"] >= indicators["macd_signal"]:
            advantages.append("MACD tarafı pozitif bölgede; momentum tamamen kopmuş görünmüyor.")
        if "oversold_rebound_watch" in signal_types:
            advantages.append("Aşırı satış bölgesinden toparlanma ihtimali izlenebilir.")
        if not advantages:
            advantages.append("Avantaj tarafı sınırlı; şu an daha çok izleme ve doğrulama modu uygun.")
        return advantages[:4]

    @staticmethod
    def _risks(technical: dict, risk_score: float) -> list[str]:
        risks = list(technical.get("reasons", []))
        if risk_score >= 65:
            risks.append("Risk skoru yüksek; hareket yakalansa bile pozisyon boyutu ve stop disiplini kritik.")
        elif risk_score >= 45:
            risks.append("Risk orta bölgede; sinyal tek başına yeterli değil, piyasa genel yönüyle doğrulanmalı.")
        else:
            risks.append("Risk düşük görünüyor ama bu risksiz olduğu anlamına gelmez; piyasa ani yön değiştirebilir.")
        return risks[:4]

    @staticmethod
    def _suggest_asset_alerts(symbol: str, technical: dict, close: float, opportunity_score: float, risk_score: float) -> list[dict]:
        indicators = technical.get("indicators", {})
        alerts = [
            {
                "symbol": symbol,
                "metric": "opportunity_score",
                "condition": ">=",
                "threshold": max(70, round(opportunity_score + 5, 2)),
                "title": f"{symbol} fırsat skoru güçlenirse haber ver",
            },
            {
                "symbol": symbol,
                "metric": "risk_score",
                "condition": ">=",
                "threshold": max(65, round(risk_score + 10, 2)),
                "title": f"{symbol} risk baskısı yükselirse uyar",
            },
        ]
        if indicators.get("sma_20"):
            alerts.append(
                {
                    "symbol": symbol,
                    "metric": "price",
                    "condition": "crosses_above",
                    "threshold": round(float(indicators["sma_20"]), 4),
                    "title": f"{symbol} SMA20 üstüne çıkarsa izle",
                }
            )
        elif close:
            alerts.append(
                {
                    "symbol": symbol,
                    "metric": "price",
                    "condition": ">=",
                    "threshold": round(close * 1.03, 4),
                    "title": f"{symbol} %3 yükselirse haber ver",
                }
            )
        return alerts[:3]

    @staticmethod
    def _market_summary(regime: str, avg_technical: float, avg_risk: float, avg_volume: float) -> str:
        if regime == "risk_on":
            return "Piyasa teknik olarak canlı; risk baskısı yönetilebilir bölgede. Fırsatlar var ama kör alım modu hâlâ yasaklı bölge."
        if regime == "risk_off":
            return "Piyasa risk baskısı yüksek bölgede. Yeni fırsatlar çıkabilir ama önce sermaye koruma filtresi çalışmalı."
        return f"Piyasa karışık modda. Teknik sağlık {avg_technical}/100, risk baskısı {avg_risk}/100, hacim ısısı {avg_volume}/100; seçici ilerlemek daha mantıklı."

    def _suggest_alerts(self, radar: list[dict]) -> list[dict]:
        suggestions: list[dict] = []
        for asset in radar[:5]:
            suggestions.extend(asset["suggested_alerts"][:2])
        return suggestions[:8]

    @staticmethod
    def _to_radar_item(asset: dict) -> dict:
        return {
            "symbol": asset["symbol"],
            "name": asset["name"],
            "label": asset["label"],
            "opportunity_score": asset["opportunity_score"],
            "risk_level": asset["risk_level"],
            "risk_score": asset["risk_score"],
            "technical_score": asset["technical_score"],
            "change_24h_pct": asset["change_24h_pct"],
            "summary": asset["plain_language_summary"],
            "top_advantage": asset["advantages"][0],
            "top_risk": asset["risks"][0],
            "signals": asset["signals"],
            "suggested_alerts": asset["suggested_alerts"],
            "is_watchlisted": asset["is_watchlisted"],
            "data_source": asset["data_source"],
        }
