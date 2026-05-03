from __future__ import annotations

from dataclasses import asdict, dataclass

from .enums import Decision, MarketRegime, RiskLevel


@dataclass
class EngineResult:
    decision: Decision
    confidence: float


@dataclass
class RiskResult:
    level: RiskLevel
    score: float


@dataclass
class RegimeResult:
    regime: MarketRegime
    probability: float


@dataclass
class TechnicalIndicatorSnapshot:
    close: float
    sma_20: float | None
    sma_50: float | None
    ema_12: float | None
    ema_26: float | None
    rsi_14: float | None
    macd: float | None
    macd_signal: float | None
    macd_histogram: float | None
    bollinger_upper: float | None
    bollinger_middle: float | None
    bollinger_lower: float | None
    atr_14: float | None
    volume_ratio: float | None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class TechnicalSignalResult:
    signal_score: float
    trend_score: float
    momentum_score: float
    volatility_score: float
    volume_score: float
    decision_hint: Decision
    direction: str
    indicators: TechnicalIndicatorSnapshot
    flags: list[str]
    reasons: list[str]

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["decision_hint"] = self.decision_hint.value
        return payload


@dataclass
class ScenarioTarget:
    name: str
    direction: str
    price: float

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MonteCarloResult:
    current_price: float
    horizon_days: int
    simulations: int
    terminal_prices: dict
    terminal_returns: dict
    touch_probabilities: dict
    terminal_probabilities: dict
    expected_return: float
    median_return: float
    probability_of_profit: float
    probability_of_loss: float
    expected_max_drawdown: float
    var_5: float
    cvar_5: float
    uncertainty_score: float
    model_parameters: dict

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RiskResult:
    risk_score: float
    risk_level: RiskLevel
    volatility_risk: float
    drawdown_risk: float
    downside_risk: float
    suggested_stop_loss_pct: float
    worst_case_return_p05: float
    reasons: list[str]
    warnings: list[str]

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["risk_level"] = self.risk_level.value
        return payload
