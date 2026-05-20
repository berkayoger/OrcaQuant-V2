from __future__ import annotations

from app.core.errors.exceptions import OrcaQuantError


class MarketDataProviderError(OrcaQuantError):
    status_code = 502
    error_code = "market_data_provider_error"
