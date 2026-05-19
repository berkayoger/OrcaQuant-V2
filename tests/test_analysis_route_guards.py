from app.extensions import db
from app.models.plan import Plan
from app.models.usage import DailyUsage, FeatureLimit
from app.models.user import User


def test_analysis_requires_auth(client):
    res = client.get('/api/v1/analysis/BTC/technical')
    assert res.status_code == 401


def test_analysis_increments_usage_on_success(app, client, monkeypatch):
    with app.app_context():
        reg = client.post('/api/v1/auth/register', json={"email": "ana@example.com", "password": "password123"}).get_json()
        user = User.query.filter_by(id=reg["user"]["id"]).one()
        plan = Plan(code="free", name="Free")
        db.session.add(plan)
        db.session.flush()
        db.session.add(FeatureLimit(plan_id=plan.id, feature_key="technical_analysis", daily_quota=5, enabled=True))
        user.plan_id = plan.id
        db.session.commit()

        monkeypatch.setattr(
            "app.services.analysis.asset_analysis_service.AssetAnalysisService.run_technical_analysis",
            lambda self, symbol, timeframe, limit: {"symbol": symbol, "ok": True},
        )

        headers = {"Authorization": f"Bearer {reg['access_token']}"}
        res = client.get('/api/v1/analysis/BTC/technical?limit=50', headers=headers)
        assert res.status_code == 200
        assert res.headers["X-Usage-Used"] == "1"
        usage = DailyUsage.query.filter_by(user_id=user.id, feature_key="technical_analysis").first()
        assert usage is not None and usage.used_count == 1
