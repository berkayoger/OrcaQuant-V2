from __future__ import annotations

from app.core.errors.exceptions import RateLimitError
from app.services.limits.usage_meter_service import UsageMeterService

PLAN_LIMITS: dict[str, dict[str, int]] = {
    "free": {"basic_analysis": 3},
    "pro": {"basic_analysis": 100, "scenario_lab": 20},
    "premium": {"basic_analysis": 500, "scenario_lab": 100, "portfolio_engine": 50},
}


class QuotaEnforcer:
    def __init__(self, usage_meter: UsageMeterService | None = None) -> None:
        self.usage_meter = usage_meter or UsageMeterService()

    def enforce_quota(self, user_id: str, plan: str, feature: str) -> None:
        limits = PLAN_LIMITS.get(plan, {})
        limit = limits.get(feature)
        if limit is None:
            raise RateLimitError(f"No quota configured for feature '{feature}' in plan '{plan}'")

        current = self.usage_meter.get_usage(user_id, feature)
        if current >= limit:
            raise RateLimitError("Daily quota exceeded")
