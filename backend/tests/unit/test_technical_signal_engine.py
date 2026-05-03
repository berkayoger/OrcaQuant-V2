from datetime import datetime, timedelta, UTC

import pytest

from app.core.engines.technical_signal_engine import TechnicalSignalEngine
from app.core.errors.exceptions import ValidationError


def _rows(count: int = 80) -> list[dict]:
    base = datetime(2024, 1, 1, tzinfo=UTC)
    rows = []
    for i in range(count):
        close = 100 + i * 0.8
        rows.append(
            {
                "timestamp": (base + timedelta(days=i)).isoformat(),
                "open": close - 1,
                "high": close + 2,
                "low": close - 2,
                "close": close,
                "volume": 1000 + i * 10,
            }
        )
    return rows


def test_technical_signal_engine_returns_scores_and_indicators():
    result = TechnicalSignalEngine().run(_rows())
    assert 0 <= result.signal_score <= 100
    assert result.indicators.rsi_14 is not None
    assert result.indicators.macd is not None
    assert result.indicators.sma_20 is not None
    assert result.indicators.sma_50 is not None


def test_technical_signal_engine_requires_minimum_rows():
    with pytest.raises(ValidationError):
        TechnicalSignalEngine().run(_rows(20))
