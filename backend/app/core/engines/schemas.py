from dataclasses import dataclass
from .enums import Decision, RiskLevel, MarketRegime

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
