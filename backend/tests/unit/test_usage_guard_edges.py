from app.extensions import db
from app.models.plan import Plan
from app.models.usage import DailyUsage, FeatureLimit
from app.models.user import User
from app.services.plans.seed_plans import seed_plans


def _register(client, email: str):
    return client.post('/api/v1/auth/register', json={'email': email, 'password': 'Password123'}).get_json()


def _auth(client, email: str):
    token = _register(client, email)['access_token']
    return {'Authorization': f'Bearer {token}'}


def _set_limit_for_user(email: str, feature_key: str, enabled: bool, quota: int | None, app):
    with app.app_context():
        user = User.query.filter_by(email=email).one()
        free = Plan.query.filter_by(code='free').one()
        user.plan_id = free.id
        FeatureLimit.query.filter_by(plan_id=free.id, feature_key=feature_key).delete()
        db.session.add(FeatureLimit(plan_id=free.id, feature_key=feature_key, enabled=enabled, daily_quota=quota))
        db.session.commit()
        return user.id, free.id


def test_usage_guard_fail_closed_and_headers(client, app, monkeypatch):
    def ok_payload(*args, **kwargs):
        return {'symbol': kwargs.get('symbol', 'BTCUSDT'), 'ok': True}

    monkeypatch.setattr('app.api.v1.analysis_routes.AssetAnalysisService.run_technical_analysis', ok_payload)

    path = '/api/v1/analysis/BTCUSDT/technical?limit=200'
    assert client.get(path).status_code == 401

    headers = _auth(client, 'noguardplan@example.com')
    no_plan = client.get(path, headers=headers)
    assert no_plan.status_code == 403
    assert no_plan.get_json()['error']['code'] == 'plan_required'

    with app.app_context():
        seed_plans()
        user = User.query.filter_by(email='noguardplan@example.com').one()
        free = Plan.query.filter_by(code='free').one()
        user.plan_id = free.id
        FeatureLimit.query.filter_by(plan_id=free.id, feature_key='technical_analysis').delete()
        db.session.commit()

    not_config = client.get(path, headers=headers)
    assert not_config.status_code == 403
    assert not_config.get_json()['error']['code'] == 'feature_not_configured'

    _set_limit_for_user('noguardplan@example.com', 'technical_analysis', enabled=False, quota=5, app=app)
    disabled = client.get(path, headers=headers)
    assert disabled.status_code == 403
    assert disabled.get_json()['error']['code'] == 'feature_disabled'

    _set_limit_for_user('noguardplan@example.com', 'technical_analysis', enabled=True, quota=0, app=app)
    zero_quota = client.get(path, headers=headers)
    assert zero_quota.status_code == 403
    assert zero_quota.get_json()['error']['code'] == 'feature_disabled'

    user_id, _ = _set_limit_for_user('noguardplan@example.com', 'technical_analysis', enabled=True, quota=1, app=app)
    with app.app_context():
        db.session.add(DailyUsage(user_id=user_id, feature_key='technical_analysis', usage_date=__import__('datetime').datetime.now(__import__('datetime').UTC).date(), used_count=1))
        db.session.commit()
    exhausted = client.get(path, headers=headers)
    assert exhausted.status_code == 429
    assert exhausted.get_json()['error']['code'] == 'quota_exceeded'

    with app.app_context():
        DailyUsage.query.delete()
        db.session.commit()

    success = client.get(path, headers=headers)
    assert success.status_code == 200
    assert success.headers['X-Usage-Used'] == '1'
    assert success.headers['X-Usage-Quota'] == '1'
    assert success.headers['X-Usage-Remaining'] == '0'

    again = client.get(path, headers=headers)
    assert again.status_code == 429

    monkeypatch.setattr('app.api.v1.analysis_routes.AssetAnalysisService.run_technical_analysis', lambda *a, **k: ({'error': 'bad'}, 400))
    with app.app_context():
        DailyUsage.query.delete()
        db.session.commit()
    bad = client.get(path, headers=headers)
    assert bad.status_code == 400
    with app.app_context():
        assert DailyUsage.query.count() == 0
