from datetime import UTC, date, datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from app.extensions import db
from app.models.usage import DailyUsage, FeatureLimit


class UsageRepository:
    def get_daily_usage(self, user_id: str, feature_key: str, usage_date: date | None = None) -> DailyUsage | None:
        day = usage_date or datetime.now(UTC).date()
        return DailyUsage.query.filter_by(user_id=user_id, feature_key=feature_key, usage_date=day).first()

    def upsert_increment(self, user_id: str, feature_key: str) -> DailyUsage:
        day = datetime.now(UTC).date()
        table = DailyUsage.__table__
        values = {"user_id": user_id, "feature_key": feature_key, "usage_date": day, "used_count": 1}

        dialect = db.session.bind.dialect.name if db.session.bind else ""
        if dialect == "postgresql":
            stmt = pg_insert(table).values(**values).on_conflict_do_update(
                index_elements=["user_id", "feature_key", "usage_date"],
                set_={"used_count": table.c.used_count + 1, "updated_at": datetime.now(UTC)},
            )
            db.session.execute(stmt)
        elif dialect == "sqlite":
            stmt = sqlite_insert(table).values(**values).on_conflict_do_update(
                index_elements=["user_id", "feature_key", "usage_date"],
                set_={"used_count": table.c.used_count + 1, "updated_at": datetime.now(UTC)},
            )
            db.session.execute(stmt)
        else:
            rec = self.get_daily_usage(user_id, feature_key, day)
            if not rec:
                rec = DailyUsage(user_id=user_id, feature_key=feature_key, usage_date=day, used_count=0)
                db.session.add(rec)
            rec.used_count += 1

        db.session.commit()
        return db.session.execute(
            select(DailyUsage).where(
                DailyUsage.user_id == user_id,
                DailyUsage.feature_key == feature_key,
                DailyUsage.usage_date == day,
            )
        ).scalar_one()

    def get_feature_limit(self, plan_id: str, feature_key: str) -> FeatureLimit | None:
        return FeatureLimit.query.filter_by(plan_id=plan_id, feature_key=feature_key).first()
