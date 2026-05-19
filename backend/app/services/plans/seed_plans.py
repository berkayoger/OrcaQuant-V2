from app.extensions import db
from app.models.plan import Plan
from app.models.usage import FeatureLimit

PLAN_DEFS = [
    {"code": "free", "name": "Free"},
    {"code": "basic", "name": "Basic"},
    {"code": "advanced", "name": "Advanced"},
    {"code": "premium", "name": "Premium"},
]

FEATURES = ["technical_analysis", "full_analysis", "scenario_risk", "forecast", "decision_consensus", "llm_analyze", "realtime_stream"]

QUOTAS = {
    "free":  {"technical_analysis": 10, "full_analysis": 2, "scenario_risk": 2, "forecast": 0, "decision_consensus": 0, "llm_analyze": 0, "realtime_stream": 0},
    "basic": {"technical_analysis": 100, "full_analysis": 20, "scenario_risk": 20, "forecast": 20, "decision_consensus": 10, "llm_analyze": 10, "realtime_stream": 0},
    "advanced": {"technical_analysis": 300, "full_analysis": 80, "scenario_risk": 80, "forecast": 80, "decision_consensus": 50, "llm_analyze": 50, "realtime_stream": 10},
    "premium": {"technical_analysis": 1000, "full_analysis": 300, "scenario_risk": 300, "forecast": 300, "decision_consensus": 200, "llm_analyze": 200, "realtime_stream": 100},
}


def seed_plans() -> dict:
    created = {"plans": 0, "limits": 0}
    plans_by_code: dict[str, Plan] = {}
    for p in PLAN_DEFS:
        plan = Plan.query.filter_by(code=p["code"]).one_or_none()
        if not plan:
            plan = Plan(code=p["code"], name=p["name"], is_active=True)
            db.session.add(plan)
            created["plans"] += 1
        plans_by_code[p["code"]] = plan
    db.session.flush()
    for code, plan in plans_by_code.items():
        for feature in FEATURES:
            limit = FeatureLimit.query.filter_by(plan_id=plan.id, feature_key=feature).one_or_none()
            if not limit:
                limit = FeatureLimit(plan_id=plan.id, feature_key=feature, daily_quota=QUOTAS[code][feature], enabled=QUOTAS[code][feature] > 0)
                db.session.add(limit)
                created["limits"] += 1
    db.session.commit()
    return created
