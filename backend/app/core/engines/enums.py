from enum import Enum


class Decision(str, Enum):
    STRONG_AVOID = "STRONG_AVOID"
    AVOID = "AVOID"
    WATCH = "WATCH"
    ACCUMULATE = "ACCUMULATE"
    BUY_CANDIDATE = "BUY_CANDIDATE"
    HIGH_RISK_OPPORTUNITY = "HIGH_RISK_OPPORTUNITY"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


class MarketRegime(str, Enum):
    BULL = "BULL"
    BEAR = "BEAR"
    SIDEWAYS = "SIDEWAYS"
    HIGH_VOLATILITY = "HIGH_VOLATILITY"
    PANIC = "PANIC"
    RECOVERY = "RECOVERY"


class RiskProfile(str, Enum):
    CONSERVATIVE = "CONSERVATIVE"
    BALANCED = "BALANCED"
    AGGRESSIVE = "AGGRESSIVE"
