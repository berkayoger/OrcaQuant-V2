from app.repositories.usage_repository import UsageRepository


class UsageService:
    def __init__(self, repository: UsageRepository | None = None):
        self.repository = repository or UsageRepository()

    def _build_status(self, used: int, quota: int | None, feature_key: str) -> dict:
        quota_val = quota if quota is not None else 0
        remaining = max(quota_val - used, 0) if quota_val else 0
        percent = int((used / quota_val) * 100) if quota_val else 0
        return {"feature_key": feature_key, "used": used, "quota": quota_val, "remaining": remaining, "percent": percent, "warn75": percent >= 75, "warn90": percent >= 90, "exhausted": quota_val > 0 and used >= quota_val}

    def get_status(self, user_id: str, feature_key: str, plan_id: str | None = None) -> dict:
        usage = self.repository.get_daily_usage(user_id, feature_key)
        used = usage.used_count if usage else 0
        limit = self.repository.get_feature_limit(plan_id, feature_key) if plan_id else None
        return self._build_status(used, limit.daily_quota if limit else None, feature_key)

    def check_limit(self, user_id: str, feature_key: str, plan_id: str | None = None) -> dict:
        status = self.get_status(user_id, feature_key, plan_id)
        status["limit_exists"] = bool(plan_id and self.repository.get_feature_limit(plan_id, feature_key))
        if status["limit_exists"]:
            limit = self.repository.get_feature_limit(plan_id, feature_key)
            status["feature_enabled"] = bool(limit and limit.enabled and limit.daily_quota > 0)
        else:
            status["feature_enabled"] = False
        return status

    def increment(self, user_id: str, feature_key: str, plan_id: str | None = None) -> dict:
        self.repository.upsert_increment(user_id, feature_key)
        return self.get_status(user_id, feature_key, plan_id)
