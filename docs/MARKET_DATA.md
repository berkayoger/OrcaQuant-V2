# Market Data Foundation

## Asset model summary
`Asset` now stores explicit attributes for symbol identity, descriptive naming, type, provider lineage, active state, and optional metadata JSON for future extensibility.

## Market price/OHLCV model summary
`MarketPrice` stores normalized OHLCV candles keyed by `asset_id + timestamp + timeframe + source` to prevent duplicates and support deterministic upsert behavior.

## Sample provider
A deterministic `SampleMarketDataProvider` supplies five static crypto assets (BTC, ETH, SOL, AVAX, XRP) and reproducible OHLCV candles generated from a seeded algorithm.

## Why no paid external provider yet
Sprint 4 intentionally avoids paid APIs to keep local and CI environments deterministic, avoid network variability, and provide a stable persistence baseline for future analysis engines.
