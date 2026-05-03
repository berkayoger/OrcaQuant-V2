import pytest

from app.core.engines.monte_carlo_engine import MonteCarloEngine
from app.core.engines.schemas import ScenarioTarget


def _rows(n=120):
    return [{"timestamp": f"2024-01-{(i%28)+1:02d}T00:00:00", "close": 100 + i * 0.3 + ((-1) ** i) * 0.2} for i in range(n)]


def test_monte_carlo_deterministic():
    e = MonteCarloEngine(simulations=500, random_seed=42)
    r1 = e.run(_rows(), 14)
    r2 = e.run(_rows(), 14)
    assert r1.terminal_returns["p50"] == r2.terminal_returns["p50"]


def test_monte_carlo_rejects_short_rows():
    with pytest.raises(ValueError):
        MonteCarloEngine().run(_rows(20), 14)


def test_monte_carlo_targets_and_quantiles():
    targets = [ScenarioTarget(name="up", direction="above", price=140), ScenarioTarget(name="down", direction="below", price=90)]
    res = MonteCarloEngine(simulations=300, random_seed=7).run(_rows(), 10, targets)
    assert all(k in res.terminal_prices for k in ["p01", "p05", "p99"])
    assert 0 <= res.touch_probabilities["up"] <= 1
    assert 0 <= res.terminal_probabilities["down"] <= 1
