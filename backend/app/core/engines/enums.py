from enum import Enum

class Decision(str, Enum):
    BUY="buy"; HOLD="hold"; SELL="sell"
class RiskLevel(str, Enum):
    LOW="low"; MEDIUM="medium"; HIGH="high"
class MarketRegime(str, Enum):
    BULL="bull"; BEAR="bear"; SIDEWAYS="sideways"
class RiskProfile(str, Enum):
    CONSERVATIVE="conservative"; BALANCED="balanced"; AGGRESSIVE="aggressive"
