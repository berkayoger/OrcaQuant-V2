from __future__ import annotations

import numpy as np

from app.core.engines.enums import RiskLevel
from app.core.engines.schemas import MonteCarloResult, RiskResult


class RiskManagementEngine:
    def run(self, ohlcv_rows: list[dict], monte_carlo_result: MonteCarloResult) -> RiskResult:
        rows = sorted(ohlcv_rows, key=lambda x: x.get("timestamp") or "")
        closes = np.array([float(r["close"]) for r in rows], dtype=float)
        log_returns = np.diff(np.log(closes))
        hist_vol = float(np.std(log_returns, ddof=1))

        running_max = np.maximum.accumulate(closes)
        drawdowns = closes / running_max - 1.0
        max_dd = float(abs(np.min(drawdowns)))

        volatility_risk = float(np.clip(hist_vol / 0.06 * 100.0, 0.0, 100.0))
        drawdown_risk = float(np.clip(max_dd / 0.40 * 100.0, 0.0, 100.0))
        downside_raw = (
            abs(monte_carlo_result.var_5) * 100 * 0.35
            + abs(monte_carlo_result.cvar_5) * 100 * 0.35
            + monte_carlo_result.probability_of_loss * 100 * 0.2
            + monte_carlo_result.uncertainty_score * 0.1
        )
        downside_risk = float(np.clip(downside_raw, 0.0, 100.0))

        risk_score = float(np.clip(volatility_risk * 0.3 + drawdown_risk * 0.3 + downside_risk * 0.4, 0.0, 100.0))
        if risk_score < 30:
            level = RiskLevel.LOW
        elif risk_score < 55:
            level = RiskLevel.MEDIUM
        elif risk_score < 75:
            level = RiskLevel.HIGH
        else:
            level = RiskLevel.EXTREME

        reasons = [
            f"Tarihsel volatilite göstergesi: {hist_vol:.4f}",
            f"Maksimum gerileme oranı: {max_dd:.2%}",
            f"Monte Carlo p05 getiri seviyesi: {monte_carlo_result.var_5:.2%}",
        ]
        warnings = []
        if monte_carlo_result.probability_of_loss > 0.5:
            warnings.append("Kayıp olasılığı %50 üzerinde; senaryo dağılımı dikkatle incelenmeli.")
        if monte_carlo_result.uncertainty_score > 70:
            warnings.append("Belirsizlik skoru yüksek; sonuçlar daha geniş aralıkta değişebilir.")

        return RiskResult(
            risk_score=risk_score,
            risk_level=level,
            volatility_risk=volatility_risk,
            drawdown_risk=drawdown_risk,
            downside_risk=downside_risk,
            suggested_stop_loss_pct=float(np.clip(max(3.0, abs(monte_carlo_result.var_5) * 60.0), 3.0, 35.0)),
            worst_case_return_p05=monte_carlo_result.var_5,
            reasons=reasons,
            warnings=warnings,
        )
