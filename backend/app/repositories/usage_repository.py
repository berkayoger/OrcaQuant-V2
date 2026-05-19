from datetime import UTC, date, datetime

from app.extensions import db
from app.models.usage import DailyUsage, FeatureLimit


class UsageRepository:
    def get_daily_usage(self, user_id: str, feature_key: str, usage_date: date | None = None) -> DailyUsage | None:
        day = usage_date or datetime.now(UTC).date()
        return DailyUsage.query.filter_by(user_id=user_id, feature_key=feature_key, usage_date=day).first()

    def upsert_increment(self, user_id: str, feature_key: str) -> DailyUsage:
        rec = self.get_daily_usage(user_id, feature_key)
        if not rec:
            rec = DailyUsage(user_id=user_id, feature_key=feature_key, usage_date=datetime.now(UTC).date(), used_count=0)
            db.session.add(rec)
        rec.used_count += 1
        db.session.commit()
        return rec

    def get_feature_limit(self, plan_id: str, feature_key: str) -> FeatureLimit | None:
        return FeatureLimit.query.filter_by(plan_id=plan_id, feature_key=feature_key, enabled=True).first()
