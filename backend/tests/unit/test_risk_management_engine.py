from app.core.engines.monte_carlo_engine import MonteCarloEngine
from app.core.engines.risk_management_engine import RiskManagementEngine


def _rows(n=120):
    return [{"timestamp": f"2024-02-{(i%28)+1:02d}T00:00:00", "close": 200 + i * 0.2 + ((-1) ** i) * 0.5} for i in range(n)]


def test_risk_engine_outputs_range_and_level():
    mc = MonteCarloEngine(simulations=300, random_seed=11).run(_rows(), 14)
    risk = RiskManagementEngine().run(_rows(), mc)
    assert 0 <= risk.risk_score <= 100
    assert risk.risk_level.value in {"LOW", "MEDIUM", "HIGH", "EXTREME"}
