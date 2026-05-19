from app.repositories.plan_repository import PlanRepository


class PlanService:
    def __init__(self, repository: PlanRepository | None = None):
        self.repository = repository or PlanRepository()

    def get_active_plan(self, code: str):
        return self.repository.get_by_code(code)
