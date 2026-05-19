from __future__ import annotations

from app.core.engines.enums import Decision, RiskLevel
from app.core.engines.schemas import FinalConsensusResult, MonteCarloResult, RiskResult, TechnicalSignalResult


class FinalConsensusEngine:
    """Combine technical, scenario, and risk outputs into one decision-support result."""

    def run(
        self,
        technical_result: TechnicalSignalResult,
        monte_carlo_result: MonteCarloResult,
        risk_result: RiskResult,
    ) -> FinalConsensusResult:
        technical_score = self._clamp(technical_result.signal_score)
        scenario_score = self._calculate_scenario_score(monte_carlo_result)
        risk_score = self._clamp(risk_result.risk_score)
        inverse_risk_score = 100.0 - risk_score
        opportunity_score = self._clamp(
            technical_score * 0.40 + scenario_score * 0.35 + inverse_risk_score * 0.25
        )
        confidence = self._calculate_confidence(technical_result, monte_carlo_result, risk_result)
        decision = self._map_decision(opportunity_score, risk_result.risk_level, monte_carlo_result.probability_of_loss)
        reasons = self._build_reasons(technical_result, monte_carlo_result, risk_result, scenario_score, opportunity_score)
        warnings = self._build_warnings(monte_carlo_result, risk_result)
        summary = self._build_summary(technical_score, scenario_score, risk_result.risk_level, decision)

        return FinalConsensusResult(
            decision=decision,
            confidence=round(confidence, 2),
            opportunity_score=round(opportunity_score, 2),
            risk_level=risk_result.risk_level,
            technical_score=round(technical_score, 2),
            scenario_score=round(scenario_score, 2),
            risk_score=round(risk_score, 2),
            summary=summary,
            reasons=reasons,
            warnings=warnings,
            engine_scores={
                "technical": round(technical_score, 2),
                "scenario": round(scenario_score, 2),
                "risk": round(risk_score, 2),
                "inverse_risk": round(inverse_risk_score, 2),
                "weights": {"technical": 0.40, "scenario": 0.35, "inverse_risk": 0.25},
            },
        )

    def _calculate_scenario_score(self, monte_carlo_result: MonteCarloResult) -> float:
        median_component = self._return_to_score(monte_carlo_result.median_return, scale=0.12)
        expected_component = self._return_to_score(monte_carlo_result.expected_return, scale=0.12)
        profit_component = self._clamp(monte_carlo_result.probability_of_profit * 100.0)
        uncertainty_penalty = self._clamp(monte_carlo_result.uncertainty_score) * 0.25
        raw_score = median_component * 0.30 + profit_component * 0.35 + expected_component * 0.25 + 50.0 * 0.10
        return self._clamp(raw_score - uncertainty_penalty)

    def _calculate_confidence(
        self,
        technical_result: TechnicalSignalResult,
        monte_carlo_result: MonteCarloResult,
        risk_result: RiskResult,
    ) -> float:
        component_scores = [
            technical_result.trend_score,
            technical_result.momentum_score,
            technical_result.volatility_score,
            technical_result.volume_score,
        ]
        max_gap = max(component_scores) - min(component_scores)
        technical_consistency = self._clamp(100.0 - max_gap)
        monte_carlo_certainty = self._clamp(100.0 - monte_carlo_result.uncertainty_score)
        risk_penalties = {
            RiskLevel.LOW: 0.0,
            RiskLevel.MEDIUM: 10.0,
            RiskLevel.HIGH: 25.0,
            RiskLevel.EXTREME: 45.0,
        }
        base = (
            technical_consistency * 0.35
            + monte_carlo_certainty * 0.30
            + monte_carlo_result.probability_of_profit * 100.0 * 0.20
            + (100.0 - self._clamp(risk_result.risk_score)) * 0.15
        )
        return self._clamp(base - risk_penalties.get(risk_result.risk_level, 20.0))

    def _map_decision(self, opportunity_score: float, risk_level: RiskLevel, probability_of_loss: float) -> Decision:
        if risk_level == RiskLevel.EXTREME and probability_of_loss > 0.60:
            return Decision.STRONG_AVOID
        if opportunity_score >= 75 and risk_level == RiskLevel.HIGH:
            return Decision.HIGH_RISK_OPPORTUNITY
        if risk_level == RiskLevel.EXTREME:
            return Decision.AVOID
        if opportunity_score >= 75 and risk_level not in {RiskLevel.HIGH, RiskLevel.EXTREME}:
            return Decision.ACCUMULATE
        if opportunity_score >= 60:
            return Decision.WATCH
        if opportunity_score >= 40:
            return Decision.WATCH
        return Decision.AVOID

    def _build_summary(
        self,
        technical_score: float,
        scenario_score: float,
        risk_level: RiskLevel,
        decision: Decision,
    ) -> str:
        technical_text = "pozitif" if technical_score >= 60 else "zayıf" if technical_score < 40 else "nötr"
        scenario_text = "destekleyici" if scenario_score >= 60 else "sınırlı" if scenario_score < 40 else "dengeli"
        if decision == Decision.HIGH_RISK_OPPORTUNITY:
            return (
                f"Teknik görünüm {technical_text} ve senaryo sonucu {scenario_text}; "
                "risk seviyesi yüksek olduğu için sonuç izleme odaklı değerlendirilmelidir."
            )
        if risk_level in {RiskLevel.HIGH, RiskLevel.EXTREME}:
            risk_text = "çok yüksek" if risk_level == RiskLevel.EXTREME else "yüksek"
            return (
                f"Teknik görünüm {technical_text}, ancak risk seviyesi {risk_text} olduğu için "
                "değerlendirme temkinli ve karar desteği odaklı ele alınmalıdır."
            )
        return (
            f"Teknik görünüm {technical_text} ve senaryo sonucu {scenario_text}; "
            "konsensüs çıktısı karar desteği amacıyla izlenebilir."
        )

    def _build_reasons(
        self,
        technical_result: TechnicalSignalResult,
        monte_carlo_result: MonteCarloResult,
        risk_result: RiskResult,
        scenario_score: float,
        opportunity_score: float,
    ) -> list[str]:
        reasons = [
            f"Teknik skor {technical_result.signal_score:.1f}/100 seviyesinde hesaplandı.",
            f"Senaryo skoru {scenario_score:.1f}/100; medyan getiri {monte_carlo_result.median_return:.2%}.",
            f"Kâr olasılığı {monte_carlo_result.probability_of_profit:.1%}, kayıp olasılığı {monte_carlo_result.probability_of_loss:.1%}.",
            f"Risk skoru {risk_result.risk_score:.1f}/100 ve risk seviyesi {risk_result.risk_level.value}.",
            f"Birleşik fırsat skoru {opportunity_score:.1f}/100 olarak dengelendi.",
        ]
        if technical_result.reasons:
            reasons.append(technical_result.reasons[0])
        return reasons[:6]

    def _build_warnings(self, monte_carlo_result: MonteCarloResult, risk_result: RiskResult) -> list[str]:
        warnings = list(risk_result.warnings)
        if monte_carlo_result.uncertainty_score > 70:
            warnings.append("Belirsizlik skoru 70 üzerinde; sonuç aralığı geniş değerlendirilmeli.")
        if monte_carlo_result.probability_of_loss > 0.55:
            warnings.append("Kayıp olasılığı %55 üzerinde; aşağı yönlü senaryolar ayrıca incelenmeli.")
        return list(dict.fromkeys(warnings))

    @staticmethod
    def _return_to_score(value: float, scale: float) -> float:
        return FinalConsensusEngine._clamp(50.0 + (value / scale) * 50.0)

    @staticmethod
    def _clamp(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
        return float(max(lower, min(upper, value)))
