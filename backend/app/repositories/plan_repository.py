from app.models.plan import Plan


class PlanRepository:
    def get_by_code(self, code: str) -> Plan | None:
        return Plan.query.filter_by(code=code, is_active=True).first()
