from app.extensions import db
from app.models.plan import Plan
from app.models.usage import FeatureLimit
from app.models.user import User


def _register(client, email: str):
    return client.post('/api/v1/auth/register', json={'email': email, 'password': 'Password123'}).get_json()


def _admin_headers(client, app, email='admin@example.com'):
    token = _register(client, email)['access_token']
    with app.app_context():
        user = User.query.filter_by(email=email).one()
        user.role = 'admin'
        db.session.commit()
    return {'Authorization': f'Bearer {token}'}


def _user_headers(client, email='user@example.com'):
    token = _register(client, email)['access_token']
    return {'Authorization': f'Bearer {token}'}


def test_admin_users_requires_admin(client, app):
    assert client.get('/api/v1/admin/users').status_code == 401
    assert client.get('/api/v1/admin/users', headers=_user_headers(client)).status_code == 403

    headers = _admin_headers(client, app)
    res = client.get('/api/v1/admin/users?page=1&per_page=10', headers=headers)
    assert res.status_code == 200
    payload = res.get_json()['data']
    assert 'items' in payload
    assert 'pagination' in payload


def test_admin_dashboard_requires_admin(client, app):
    assert client.get('/api/v1/admin/dashboard/').status_code == 401
    assert client.get('/api/v1/admin/dashboard/', headers=_user_headers(client, 'basic2@example.com')).status_code == 403

    headers = _admin_headers(client, app, 'admin-dashboard@example.com')
    res = client.get('/api/v1/admin/dashboard/', headers=headers)
    assert res.status_code == 200
    data = res.get_json()['data']
    for key in ('users', 'plans', 'active_plans', 'feature_limits', 'payment_transactions'):
        assert key in data


def test_limits_status_response(client, app):
    headers = _user_headers(client, 'limits-status@example.com')

    with app.app_context():
        user = User.query.filter_by(email='limits-status@example.com').one()
        plan = Plan(code='starter', name='Starter', is_active=True, sort_order=1)
        db.session.add(plan)
        db.session.flush()
        user.plan_id = plan.id
        db.session.add(FeatureLimit(plan_id=plan.id, feature_key='technical_analysis', daily_quota=10, enabled=True))
        db.session.commit()

    res = client.get('/api/v1/limits/status', headers=headers)
    assert res.status_code == 200
    payload = res.get_json()
    assert payload['plan_id'] is not None
    assert payload['plan']['code'] == 'starter'
    assert len(payload['features']) == 1
    feature = payload['features'][0]
    for key in ('feature_key', 'used', 'quota', 'remaining', 'percent', 'warning_level', 'exhausted'):
        assert key in feature


def test_limits_status_no_plan_returns_null_plan_and_empty_features(client):
    headers = _user_headers(client, 'limits-no-plan@example.com')
    res = client.get('/api/v1/limits/status', headers=headers)
    assert res.status_code == 200
    payload = res.get_json()
    assert payload['plan_id'] is None
    assert payload['plan'] is None
    assert payload['features'] == []


def test_limits_status_warning_levels(client, app):
    headers = _user_headers(client, 'limits-warning@example.com')
    with app.app_context():
        user = User.query.filter_by(email='limits-warning@example.com').one()
        plan = Plan(code='warning', name='Warning', is_active=True, sort_order=2)
        db.session.add(plan)
        db.session.flush()
        user.plan_id = plan.id
        db.session.add(FeatureLimit(plan_id=plan.id, feature_key='technical_analysis', daily_quota=100, enabled=True))
        db.session.commit()

    for used, expected in ((75, '75'), (90, '90'), (100, '100')):
        with app.app_context():
            from app.models.usage import DailyUsage
            row = DailyUsage.query.filter_by(feature_key='technical_analysis').first()
            if row is None:
                row = DailyUsage(user_id=User.query.filter_by(email='limits-warning@example.com').one().id, feature_key='technical_analysis', used_count=used)
                db.session.add(row)
            row.used_count = used
            db.session.commit()
        res = client.get('/api/v1/limits/status', headers=headers)
        feature = res.get_json()['features'][0]
        assert feature['warning_level'] == expected
        assert feature['exhausted'] is (used >= 100)


def test_limits_status_plan_without_feature_limits_returns_empty_features(client, app):
    headers = _user_headers(client, 'limits-plan-no-feature@example.com')
    with app.app_context():
        user = User.query.filter_by(email='limits-plan-no-feature@example.com').one()
        plan = Plan(code='solo', name='Solo', is_active=True, sort_order=3)
        db.session.add(plan)
        db.session.flush()
        user.plan_id = plan.id
        db.session.commit()

    res = client.get('/api/v1/limits/status', headers=headers)
    payload = res.get_json()
    assert payload['plan']['id'] is not None
    assert payload['plan']['code'] == 'solo'
    assert payload['features'] == []


def test_limits_status_quota_zero_disabled_feature_behavior(client, app):
    headers = _user_headers(client, 'limits-zero@example.com')
    with app.app_context():
        user = User.query.filter_by(email='limits-zero@example.com').one()
        plan = Plan(code='zero', name='Zero', is_active=True, sort_order=4)
        db.session.add(plan)
        db.session.flush()
        user.plan_id = plan.id
        db.session.add(FeatureLimit(plan_id=plan.id, feature_key='scenario_risk', daily_quota=0, enabled=False))
        db.session.commit()

    res = client.get('/api/v1/limits/status', headers=headers)
    feature = res.get_json()['features'][0]
    assert feature['quota'] == 0
    assert feature['used'] == 0
    assert feature['remaining'] == 0
    assert feature['percent'] == 0
    assert feature['warning_level'] == '100'
    assert feature['exhausted'] is True


def test_limits_status_warning_level_null_below_threshold(client, app):
    headers = _user_headers(client, 'limits-warning-null@example.com')
    with app.app_context():
        user = User.query.filter_by(email='limits-warning-null@example.com').one()
        plan = Plan(code='warnnull', name='WarnNull', is_active=True, sort_order=5)
        db.session.add(plan)
        db.session.flush()
        user.plan_id = plan.id
        db.session.add(FeatureLimit(plan_id=plan.id, feature_key='full_analysis', daily_quota=100, enabled=True))
        db.session.commit()

    res = client.get('/api/v1/limits/status', headers=headers)
    feature = res.get_json()['features'][0]
    assert feature['warning_level'] is None
    assert feature['exhausted'] is False
