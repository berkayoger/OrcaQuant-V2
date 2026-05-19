from app.repositories.usage_repository import UsageRepository


class UsageService:
    def __init__(self, repository: UsageRepository | None = None):
        self.repository = repository or UsageRepository()

    def _build_status(self, used: int, quota: int | None) -> dict:
        quota = quota or 0
        remaining = max(quota - used, 0) if quota else 0
        percent = int((used / quota) * 100) if quota else 0
        return {"used": used, "quota": quota, "remaining": remaining, "percent": percent, "warn75": percent >= 75, "warn90": percent >= 90, "exhausted": quota > 0 and used >= quota}

    def get_status(self, user_id: str, feature_key: str, plan_id: str | None = None) -> dict:
        usage = self.repository.get_daily_usage(user_id, feature_key)
        used = usage.used_count if usage else 0
        limit = self.repository.get_feature_limit(plan_id, feature_key) if plan_id else None
        return self._build_status(used, limit.daily_quota if limit else None)

    def check_limit(self, user_id: str, feature_key: str, plan_id: str | None = None) -> dict:
        return self.get_status(user_id, feature_key, plan_id)

    def increment(self, user_id: str, feature_key: str, plan_id: str | None = None) -> dict:
        self.repository.upsert_increment(user_id, feature_key)
        return self.get_status(user_id, feature_key, plan_id)
