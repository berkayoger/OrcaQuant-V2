import pytest

from app.core.security.runtime_config import validate_runtime_config
from app.extensions import limiter
from app.factory import create_app


def test_invalid_cors_origin_fails_fast(monkeypatch):
    app = create_app("testing")
    app.config["CORS_ALLOWED_ORIGINS"] = ["not-a-url"]

    with pytest.raises(RuntimeError, match="Invalid CORS origin format"):
        validate_runtime_config(app, "testing")


def test_default_rate_limit_policy_is_configured():
    assert len(limiter.limit_manager.default_limits) == 2
