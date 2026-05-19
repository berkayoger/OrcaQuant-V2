from app.core.engines.enums import Decision, RiskLevel
from app.core.engines.final_consensus_engine import FinalConsensusEngine
from app.core.engines.schemas import (
    MonteCarloResult,
    RiskResult,
    TechnicalIndicatorSnapshot,
    TechnicalSignalResult,
)


def _technical(score=80.0):
    return TechnicalSignalResult(
        signal_score=score,
        trend_score=82.0,
        momentum_score=78.0,
        volatility_score=75.0,
        volume_score=80.0,
        decision_hint=Decision.ACCUMULATE,
        direction="uptrend",
        indicators=TechnicalIndicatorSnapshot(
            close=100.0,
            sma_20=95.0,
            sma_50=90.0,
            ema_12=98.0,
            ema_26=94.0,
            rsi_14=58.0,
            macd=1.2,
            macd_signal=0.8,
            macd_histogram=0.4,
            bollinger_upper=110.0,
            bollinger_middle=100.0,
            bollinger_lower=90.0,
            atr_14=3.0,
            volume_ratio=1.1,
        ),
        flags=[],
        reasons=["Teknik göstergeler destekleyici."],
    )


def _monte_carlo(profit=0.72, loss=0.28, uncertainty=25.0, expected=0.08, median=0.07):
    return MonteCarloResult(
        current_price=100.0,
        horizon_days=14,
        simulations=3000,
        terminal_prices={"p50": 107.0},
        terminal_returns={"p50": median},
        touch_probabilities={},
        terminal_probabilities={},
        expected_return=expected,
        median_return=median,
        probability_of_profit=profit,
        probability_of_loss=loss,
        expected_max_drawdown=-0.06,
        var_5=-0.12,
        cvar_5=-0.18,
        uncertainty_score=uncertainty,
        model_parameters={"drift": 0.01, "volatility": 0.02},
    )


def _risk(level=RiskLevel.MEDIUM, score=45.0):
    return RiskResult(
        risk_score=score,
        risk_level=level,
        volatility_risk=35.0,
        drawdown_risk=40.0,
        downside_risk=50.0,
        suggested_stop_loss_pct=8.0,
        worst_case_return_p05=-0.12,
        reasons=["Risk seviyesi dengeli."],
        warnings=["Risk uyarısı."],
    )


def test_final_consensus_returns_scores_and_decision():
    result = FinalConsensusEngine().run(_technical(), _monte_carlo(), _risk())

    assert result.decision in Decision
    assert 0 <= result.confidence <= 100
    assert 0 <= result.opportunity_score <= 100
    assert result.to_dict()["decision"] == result.decision.value
    assert result.to_dict()["risk_level"] == result.risk_level.value


def test_extreme_risk_prevents_accumulate():
    result = FinalConsensusEngine().run(
        _technical(95.0),
        _monte_carlo(profit=0.85, loss=0.15, uncertainty=10.0, expected=0.18, median=0.16),
        _risk(level=RiskLevel.EXTREME, score=82.0),
    )

    assert result.decision != Decision.ACCUMULATE
    assert result.decision in {Decision.AVOID, Decision.STRONG_AVOID}


def test_high_risk_high_opportunity_can_be_labeled_high_risk_opportunity():
    result = FinalConsensusEngine().run(
        _technical(92.0),
        _monte_carlo(profit=0.90, loss=0.10, uncertainty=5.0, expected=0.20, median=0.18),
        _risk(level=RiskLevel.HIGH, score=55.0),
    )

    assert result.decision == Decision.HIGH_RISK_OPPORTUNITY
