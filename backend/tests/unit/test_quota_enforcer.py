import pytest

from app.core.errors.exceptions import RateLimitError
from app.services.limits.quota_enforcer import QuotaEnforcer
from app.services.limits.usage_meter_service import UsageMeterService


def test_quota_enforcement_blocks_after_limit() -> None:
    meter = UsageMeterService()
    enforcer = QuotaEnforcer(meter)

    user_id = "u-1"
    feature = "basic_analysis"
    for _ in range(3):
        enforcer.enforce_quota(user_id, "free", feature)
        meter.increment_usage(user_id, feature)

    with pytest.raises(RateLimitError):
        enforcer.enforce_quota(user_id, "free", feature)
