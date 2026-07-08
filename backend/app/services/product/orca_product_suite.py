from __future__ import annotations

from collections import Counter
from typing import Any

from app.models.alert_rule import AlertRule
from app.services.dashboard.market_cockpit_service import MarketCockpitService


class OrcaProductSuite:
    """Customer-facing product contracts built on top of Market Cockpit.

    The goal of this service is to expose the next product modules without
    pretending that external news, delivery providers, or historical backtests
    exist before they are wired. Where a module needs more infrastructure, the
    payload explicitly declares its boundary.
    """

    def __init__(self, cockpit_service: MarketCockpitService | None = None) -> None:
        self.cockpit_service = cockpit_service or MarketCockpitService()

    def build_daily_brief(self, symbols: list[str] | None = None) -> dict:
        cockpit = self.cockpit_service.build_cockpit(symbols=symbols)
        leaders = cockpit["radar"][:3]
        risk_flags = [item for item in cockpit["radar"] if item["risk_score"] >= 65][:3]
        return {
            "module": "orca_daily_brief",
            "status": "customer_mvp_contract",
            "investment_advice": False,
            "market_mode": cockpit["market_overview"]["regime"],
            "headline": self._brief_headline(cockpit),
            "summary": cockpit["market_overview"]["summary"],
            "leaders": leaders,
            "risk_flags": risk_flags,
            "watchpoints": cockpit["market_overview"]["watchpoints"],
            "suggested_alerts": cockpit["suggested_alerts"][:5],
            "delivery_ready": ["in_app"],
            "external_delivery_pending": ["email", "telegram", "push", "sms"],
            "data_boundary": "Generated from Market Cockpit signals; external news and social sentiment are not included yet.",
        }

    def build_asset_detail(self, symbol: str) -> dict:
        clean = self._normalize_symbol(symbol)
        cockpit = self.cockpit_service.build_cockpit(symbols=[clean])
        asset = cockpit["assets"][0]
        return {
            "module": "asset_detail",
            "status": "customer_mvp_contract",
            "investment_advice": False,
            "asset": asset,
            "chart_summary": {
                "price": asset["price"],
                "change_24h_pct": asset["change_24h_pct"],
                "technical_score": asset["technical_score"],
                "risk_score": asset["risk_score"],
                "opportunity_score": asset["opportunity_score"],
                "data_source": asset["data_source"],
            },
            "tabs": ["overview", "technical", "risk", "alerts", "notes"],
            "quick_actions": [
                {"type": "watchlist", "label": f"{clean} takip listesine ekle"},
                {"type": "alert", "label": f"{clean} için alarm kur", "suggestions": asset["suggested_alerts"]},
                {"type": "compare", "label": f"{clean} riskini BTC ile karşılaştır"},
            ],
            "data_boundary": "Historical chart rendering is frontend/provider work; this endpoint returns the asset-detail contract and latest technical snapshot.",
        }

    def build_radar_variants(self, symbols: list[str] | None = None) -> dict:
        cockpit = self.cockpit_service.build_cockpit(symbols=symbols)
        assets = cockpit["assets"]
        return {
            "module": "orca_radar_v2",
            "status": "customer_mvp_contract",
            "investment_advice": False,
            "variants": {
                "daily_top_5": self._rank(assets, "opportunity_score", reverse=True, limit=5),
                "momentum_radar": self._rank([asset for asset in assets if asset["change_24h_pct"] > 0], "change_24h_pct", reverse=True),
                "risk_radar": self._rank(assets, "risk_score", reverse=True),
                "volume_radar": self._rank(assets, "volume_score", reverse=True),
                "trend_radar": self._rank(assets, "technical_score", reverse=True),
                "reversal_watch": [asset for asset in assets if any(signal["type"] == "oversold_rebound_watch" for signal in asset["signals"])],
                "breakout_watch": [asset for asset in assets if any(signal["type"] in {"momentum_burst", "volume_spike"} for signal in asset["signals"])],
                "pump_risk_watch": self._pump_risk_watch(assets),
            },
            "labels": ["İzlenebilir", "Riskli fırsat", "Trend güçlü", "Dikkatli ol", "Henüz erken", "Kaçırılmış olabilir", "Manipülasyon riski yüksek"],
            "data_boundary": "Whale, funding, open-interest and social hype inputs are planned; current Radar v2 is based on price/volume/technical cockpit signals.",
        }

    def build_portfolio_assistant(self, holdings: list[dict[str, Any]]) -> dict:
        normalized = self._normalize_holdings(holdings)
        symbols = [item["symbol"] for item in normalized]
        cockpit = self.cockpit_service.build_cockpit(symbols=symbols) if symbols else self.cockpit_service.build_cockpit()
        assets_by_symbol = {asset["symbol"]: asset for asset in cockpit["assets"]}
        enriched = []
        for holding in normalized:
            asset = assets_by_symbol.get(holding["symbol"])
            if not asset:
                continue
            allocation = holding["allocation_pct"]
            enriched.append(
                {
                    **holding,
                    "risk_score": asset["risk_score"],
                    "opportunity_score": asset["opportunity_score"],
                    "risk_contribution": round(allocation * asset["risk_score"] / 100, 2),
                    "label": asset["label"],
                    "top_risk": asset["risks"][0],
                    "top_advantage": asset["advantages"][0],
                }
            )
        portfolio_risk = round(sum(item["risk_contribution"] for item in enriched), 2) if enriched else 0
        concentration = max((item["allocation_pct"] for item in enriched), default=0)
        return {
            "module": "portfolio_assistant",
            "status": "customer_mvp_contract",
            "investment_advice": False,
            "portfolio_risk_score": portfolio_risk,
            "concentration_score": concentration,
            "holdings": enriched,
            "insights": self._portfolio_insights(enriched, portfolio_risk, concentration),
            "suggested_alerts": self._portfolio_alerts(enriched),
            "data_boundary": "This is risk explanation and decision support only; it does not rebalance or recommend buy/sell actions.",
        }

    def build_plan_entitlements(self) -> dict:
        return {
            "module": "plan_entitlements",
            "status": "customer_mvp_contract",
            "plans": [
                {
                    "key": "free",
                    "name": "Free",
                    "limits": {"watchlist_symbols": 5, "active_alerts": 3, "radar_variants": 2, "portfolio_slots": 0},
                    "features": ["Market Cockpit", "Basic Orca Radar", "In-app notifications", "Local alert drafts"],
                },
                {
                    "key": "pro",
                    "name": "Pro",
                    "limits": {"watchlist_symbols": 25, "active_alerts": 25, "radar_variants": 6, "portfolio_slots": 3},
                    "features": ["Advanced Radar", "Alert Rule Engine", "Daily Brief", "Portfolio Assistant", "Notification Center", "Email/Telegram delivery contract"],
                },
                {
                    "key": "premium",
                    "name": "Premium",
                    "limits": {"watchlist_symbols": "unlimited", "active_alerts": "unlimited", "radar_variants": "all", "portfolio_slots": "unlimited"},
                    "features": ["Backtest reports", "Whale/funding/OI radar", "Admin analytics", "Priority data providers", "Advanced portfolio risk", "External delivery adapters"],
                },
            ],
        }

    def build_admin_analytics(self) -> dict:
        rules = AlertRule.query.all()
        by_metric = Counter((rule.data or {}).get("metric") for rule in rules)
        by_symbol = Counter((rule.data or {}).get("symbol") for rule in rules)
        triggered = sum(int((rule.data or {}).get("trigger_count") or 0) for rule in rules)
        enabled = sum(1 for rule in rules if (rule.data or {}).get("enabled", True))
        return {
            "module": "admin_product_analytics",
            "status": "customer_mvp_contract",
            "alert_rules": {
                "total": len(rules),
                "enabled": enabled,
                "disabled": len(rules) - enabled,
                "trigger_count": triggered,
                "by_metric": dict(by_metric),
                "top_symbols": by_symbol.most_common(10),
            },
            "product_health": [
                {"key": "alert_engine", "status": "active"},
                {"key": "notification_center", "status": "active"},
                {"key": "in_app_delivery", "status": "active"},
                {"key": "external_delivery", "status": "needs_provider_config"},
                {"key": "realtime_streaming", "status": "planned"},
                {"key": "external_sentiment", "status": "planned"},
                {"key": "backtest_reports", "status": "contract_ready"},
            ],
        }

    def build_feature_suite(self, symbols: list[str] | None = None) -> dict:
        sample_portfolio = [
            {"symbol": "BTC", "allocation_pct": 45},
            {"symbol": "ETH", "allocation_pct": 30},
            {"symbol": "SOL", "allocation_pct": 25},
        ]
        return {
            "module": "orcaquant_product_suite",
            "status": "customer_mvp_contract",
            "investment_advice": False,
            "daily_brief": self.build_daily_brief(symbols=symbols),
            "radar_v2": self.build_radar_variants(symbols=symbols),
            "portfolio_assistant": self.build_portfolio_assistant(sample_portfolio),
            "plans": self.build_plan_entitlements()["plans"],
            "admin_analytics": self.build_admin_analytics(),
            "feature_boundaries": {
                "notification_delivery": "In-app notification persistence is active; email/push/Telegram sender adapters are next.",
                "live_provider_expansion": "Provider interface exists; additional providers and realtime streaming are next.",
                "news_sentiment": "Contract planned; external news/social sources not wired yet.",
                "backtest": "Contract planned; historical provider and signal outcome tracking are next.",
            },
        }

    @staticmethod
    def _normalize_symbol(symbol: str) -> str:
        return "".join(ch for ch in str(symbol).upper().strip() if ch.isalnum())

    @staticmethod
    def _rank(assets: list[dict], key: str, reverse: bool = True, limit: int = 5) -> list[dict]:
        return sorted(assets, key=lambda item: item.get(key, 0), reverse=reverse)[:limit]

    @staticmethod
    def _pump_risk_watch(assets: list[dict]) -> list[dict]:
        risky = []
        for asset in assets:
            volume_hot = asset["volume_score"] >= 70
            price_hot = asset["change_24h_pct"] >= 4
            high_risk = asset["risk_score"] >= 65
            if (volume_hot and price_hot) or (volume_hot and high_risk):
                risky.append({**asset, "label": "Manipülasyon riski yüksek"})
        return sorted(risky, key=lambda item: item["risk_score"], reverse=True)[:5]

    @staticmethod
    def _brief_headline(cockpit: dict) -> str:
        leader = cockpit["radar"][0]
        regime = cockpit["market_overview"]["regime"]
        return f"Piyasa {regime} modunda; {leader['symbol']} radarın üst sırasında, risk skoru {leader['risk_score']}/100."

    @staticmethod
    def _normalize_holdings(holdings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        cleaned = []
        total_weight = 0.0
        for item in holdings or []:
            symbol = OrcaProductSuite._normalize_symbol(item.get("symbol") or "")
            if not symbol:
                continue
            allocation = item.get("allocation_pct")
            try:
                allocation = float(allocation)
            except (TypeError, ValueError):
                allocation = 0.0
            if allocation > 0:
                total_weight += allocation
                cleaned.append({"symbol": symbol, "allocation_pct": allocation})
        if total_weight and abs(total_weight - 100) > 0.01:
            cleaned = [{**item, "allocation_pct": round(item["allocation_pct"] / total_weight * 100, 2)} for item in cleaned]
        return cleaned[:20]

    @staticmethod
    def _portfolio_insights(holdings: list[dict], portfolio_risk: float, concentration: float) -> list[str]:
        insights = []
        if concentration >= 50:
            insights.append("Portföy tek varlığa yoğunlaşmış görünüyor; senaryo riski artabilir.")
        if portfolio_risk >= 65:
            insights.append("Toplam risk baskısı yüksek; alarm ve sermaye koruma filtresi aktif takip edilmeli.")
        elif portfolio_risk >= 40:
            insights.append("Risk orta bölgede; yüksek beta varlıkların piyasa geneliyle birlikte izlenmesi gerekir.")
        else:
            insights.append("Risk baskısı düşük görünüyor ancak bu risksiz olduğu anlamına gelmez.")
        high_risk = [item["symbol"] for item in holdings if item["risk_score"] >= 65]
        if high_risk:
            insights.append(f"Yüksek risk katkısı olan varlıklar: {', '.join(high_risk)}.")
        return insights

    @staticmethod
    def _portfolio_alerts(holdings: list[dict]) -> list[dict]:
        alerts = []
        for item in holdings[:5]:
            alerts.append(
                {
                    "symbol": item["symbol"],
                    "metric": "risk_score",
                    "condition": ">=",
                    "threshold": max(65, round(item["risk_score"] + 8, 2)),
                    "title": f"{item['symbol']} portföy riskini artırırsa uyar",
                }
            )
        return alerts
