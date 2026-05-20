from app.repositories.usage_repository import UsageRepository


class UsageService:
    def __init__(self, repository: UsageRepository | None = None):
        self.repository = repository or UsageRepository()

    def _build_status(self, used: int, feature_key: str, limit=None) -> dict:
        """Build stable usage payload.

        quota semantics:
        - None: no configured limit row (unknown / not configured)
        - 0: configured but disabled or no quota allocation
        """
        quota = limit.daily_quota if limit else None
        limit_exists = limit is not None
        feature_enabled = bool(limit and limit.enabled and (limit.daily_quota or 0) > 0)

        remaining = max((quota or 0) - used, 0) if quota is not None else None
        percent = int((used / quota) * 100) if quota and quota > 0 else 0
        exhausted = bool(quota is not None and quota >= 0 and used >= quota) if limit_exists else False

        return {
            "feature_key": feature_key,
            "used": used,
            "quota": quota,
            "remaining": remaining,
            "percent": percent,
            "warn75": percent >= 75,
            "warn90": percent >= 90,
            "exhausted": exhausted,
            "limit_exists": limit_exists,
            "feature_enabled": feature_enabled,
        }

    def _get_limit(self, plan_id: str | None, feature_key: str):
        return self.repository.get_feature_limit(plan_id, feature_key) if plan_id else None

    def get_status(self, user_id: str, feature_key: str, plan_id: str | None = None) -> dict:
        usage = self.repository.get_daily_usage(user_id, feature_key)
        used = usage.used_count if usage else 0
        return self._build_status(used=used, feature_key=feature_key, limit=self._get_limit(plan_id, feature_key))

    def check_limit(self, user_id: str, feature_key: str, plan_id: str | None = None) -> dict:
        usage = self.repository.get_daily_usage(user_id, feature_key)
        used = usage.used_count if usage else 0
        limit = self._get_limit(plan_id, feature_key)
        return self._build_status(used=used, feature_key=feature_key, limit=limit)

    def increment(self, user_id: str, feature_key: str, plan_id: str | None = None) -> dict:
        usage = self.repository.upsert_increment(user_id, feature_key)
        return self._build_status(used=usage.used_count, feature_key=feature_key, limit=self._get_limit(plan_id, feature_key))
