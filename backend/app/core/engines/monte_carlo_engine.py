from __future__ import annotations

import numpy as np

from app.core.engines.schemas import MonteCarloResult, ScenarioTarget


class MonteCarloEngine:
    def __init__(self, simulations: int = 3000, random_seed: int | None = 42) -> None:
        self.simulations = simulations
        self.random_seed = random_seed

    def run(self, ohlcv_rows: list[dict], horizon_days: int = 14, targets: list[ScenarioTarget] | None = None) -> MonteCarloResult:
        if len(ohlcv_rows) < 50:
            raise ValueError("At least 50 OHLCV rows are required for Monte Carlo analysis")
        rows = sorted(ohlcv_rows, key=lambda x: x.get("timestamp") or "")
        closes = np.array([float(r["close"]) for r in rows], dtype=float)
        log_returns = np.diff(np.log(closes))
        mu = float(np.mean(log_returns))
        sigma = float(np.std(log_returns, ddof=1))
        current = float(closes[-1])

        rng = np.random.default_rng(self.random_seed)
        shocks = rng.normal(mu, sigma, size=(self.simulations, horizon_days))
        cum_rets = np.cumsum(shocks, axis=1)
        paths = current * np.exp(cum_rets)
        terminal_prices = paths[:, -1]
        terminal_returns = terminal_prices / current - 1.0

        qs = [1, 5, 10, 25, 50, 75, 90, 95, 99]
        price_q = {f"p{q:02d}": float(np.percentile(terminal_prices, q)) for q in qs}
        return_q = {f"p{q:02d}": float(np.percentile(terminal_returns, q)) for q in qs}

        running_max = np.maximum.accumulate(paths, axis=1)
        drawdowns = paths / running_max - 1.0
        max_drawdowns = np.min(drawdowns, axis=1)

        touch_probs: dict[str, float] = {}
        terminal_probs: dict[str, float] = {}
        for t in targets or []:
            if t.direction == "above":
                touch_probs[t.name] = float(np.mean(np.any(paths >= t.price, axis=1)))
                terminal_probs[t.name] = float(np.mean(terminal_prices >= t.price))
            else:
                touch_probs[t.name] = float(np.mean(np.any(paths <= t.price, axis=1)))
                terminal_probs[t.name] = float(np.mean(terminal_prices <= t.price))

        var_5 = float(np.percentile(terminal_returns, 5))
        cvar_5 = float(np.mean(terminal_returns[terminal_returns <= var_5]))
        uncertainty = float(np.clip((sigma * np.sqrt(horizon_days)) / 0.15 * 100.0, 0.0, 100.0))

        return MonteCarloResult(
            current_price=current,
            horizon_days=horizon_days,
            simulations=self.simulations,
            terminal_prices=price_q,
            terminal_returns=return_q,
            touch_probabilities=touch_probs,
            terminal_probabilities=terminal_probs,
            expected_return=float(np.mean(terminal_returns)),
            median_return=float(np.median(terminal_returns)),
            probability_of_profit=float(np.mean(terminal_returns > 0)),
            probability_of_loss=float(np.mean(terminal_returns < 0)),
            expected_max_drawdown=float(np.mean(max_drawdowns)),
            var_5=var_5,
            cvar_5=cvar_5,
            uncertainty_score=uncertainty,
            model_parameters={"drift": mu, "volatility": sigma},
        )
