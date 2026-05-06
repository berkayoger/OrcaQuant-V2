# Unified Full Analysis Flow

Sprint 7 adds a unified full analysis endpoint that orchestrates the technical, scenario, risk, and final consensus layers into one response.

## Endpoint

`POST /api/v1/analysis/<symbol>/full`

Example request:

```json
{
  "timeframe": "1d",
  "limit": 200,
  "horizon_days": 14,
  "targets": [
    {"name": "target_up", "direction": "above", "price": 30000}
  ]
}
```

Validation rules:

- `limit` must be between 50 and 1000.
- `horizon_days` must be between 1 and 365.
- each target direction must be `above` or `below`.

## Service orchestration

`AssetAnalysisService.run_full_analysis` keeps the route thin and coordinates the workflow:

1. Find the asset by symbol.
2. Load OHLCV rows from the market data repository.
3. Sync sample OHLCV data through `OhlcvService` if rows are missing.
4. Run `TechnicalSignalEngine`.
5. Convert target dictionaries into `ScenarioTarget` objects.
6. Run `MonteCarloEngine`.
7. Run `RiskManagementEngine`.
8. Run `FinalConsensusEngine`.
9. Persist a general `AnalysisResult` with `analysis_type = "full"`.
10. Persist Monte Carlo, risk, and decision payloads in their dedicated repositories.
11. Return one response containing all four analysis sections.

## Response shape

```json
{
  "symbol": "BTC",
  "timeframe": "1d",
  "horizon_days": 14,
  "analysis_type": "full",
  "technical": {},
  "monte_carlo": {},
  "risk": {},
  "consensus": {},
  "saved_analysis_id": "uuid"
}
```

## Architecture boundaries

- Routes validate HTTP input and call services.
- Services orchestrate repositories and engines.
- Repositories persist and retrieve rows only.
- Engines are pure computation units and do not know about Flask or SQLAlchemy sessions.

## Decision support positioning

The full analysis response is a structured research aid. It combines model outputs into a neutral summary, reasons, warnings, and scores so the user can evaluate conditions more clearly. It does not direct a transaction or remove the need for independent judgment.
