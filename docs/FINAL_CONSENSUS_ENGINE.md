# Final Consensus Engine

The Final Consensus Engine is the product-facing decision-support layer for Sprint 7. It combines the existing technical signal, Monte Carlo scenario, and risk management outputs into a single neutral analysis result.

## What it does

- Reads already-computed engine results from the service layer.
- Produces one `FinalConsensusResult` with a decision label, confidence, opportunity score, risk level, summary, reasons, warnings, and component scores.
- Uses deterministic scoring so unit tests can validate boundaries and decision mapping.
- Communicates in neutral Turkish wording focused on observation and decision support.

## What it does not do

- It does not query the database.
- It does not access Flask requests or responses.
- It does not place trades or automate portfolio actions.
- It does not replace investor judgment, risk controls, or professional review.
- It does not present outcomes as certain.

## Inputs

The engine accepts three dataclass outputs:

1. `TechnicalSignalResult`
2. `MonteCarloResult`
3. `RiskResult`

These are created by dedicated engines and passed to the consensus engine by `AssetAnalysisService`.

## Scoring approach

The final `opportunity_score` is weighted as follows:

- 40% technical score from `TechnicalSignalResult.signal_score`
- 35% scenario score derived from median return, expected return, probability of profit, and uncertainty
- 25% inverse risk score from `100 - RiskResult.risk_score`

Confidence combines technical component consistency, Monte Carlo uncertainty, risk penalty, and probability of profit. Risk level can restrict the final label even when opportunity is high.

## Decision labels

The engine uses decision-support labels:

- `WATCH`
- `ACCUMULATE`
- `AVOID`
- `STRONG_AVOID`
- `HIGH_RISK_OPPORTUNITY`

`EXTREME` risk prevents an `ACCUMULATE` label. High risk with strong opportunity may become `HIGH_RISK_OPPORTUNITY`, signaling that any review should be more cautious.

## Example response

```json
{
  "decision": "WATCH",
  "confidence": 63.4,
  "opportunity_score": 61.2,
  "risk_level": "HIGH",
  "technical_score": 72.8,
  "scenario_score": 58.5,
  "risk_score": 67.0,
  "summary": "Teknik görünüm pozitif, ancak risk seviyesi high olduğu için değerlendirme temkinli ve karar desteği odaklı ele alınmalıdır.",
  "reasons": [
    "Teknik skor 72.8/100 seviyesinde hesaplandı.",
    "Senaryo skoru 58.5/100; medyan getiri 2.10%.",
    "Risk skoru 67.0/100 ve risk seviyesi HIGH."
  ],
  "warnings": [
    "Belirsizlik skoru 70 üzerinde; sonuç aralığı geniş değerlendirilmeli."
  ],
  "engine_scores": {
    "technical": 72.8,
    "scenario": 58.5,
    "risk": 67.0,
    "inverse_risk": 33.0
  }
}
```

## Decision support note

This output is intended to organize model signals into a clear analysis snapshot. It is not investment advice and should be interpreted together with user risk profile, portfolio context, liquidity, fees, tax considerations, and changing market conditions.
