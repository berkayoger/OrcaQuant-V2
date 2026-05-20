from app.extensions import db
from app.models.plan import Plan
from app.models.usage import FeatureLimit
from app.models.user import User
from app.services.plans.seed_plans import seed_plans


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


def test_admin_plans_authz(client, app):
    assert client.get('/api/v1/admin/plans').status_code == 401
    assert client.get('/api/v1/admin/plans', headers=_user_headers(client)).status_code == 403

    headers = _admin_headers(client, app)
    res = client.get('/api/v1/admin/plans', headers=headers)
    assert res.status_code == 200
    assert 'items' in res.get_json()['data']


def test_admin_plan_crud(client, app):
    headers = _admin_headers(client, app, 'admin2@example.com')
    create = client.post('/api/v1/admin/plans', headers=headers, json={'code': 'pro_plus', 'name': 'Pro Plus', 'sort_order': 9})
    assert create.status_code == 201
    created = create.get_json()['data']

    patch = client.patch(f"/api/v1/admin/plans/{created['id']}", headers=headers, json={'name': 'Pro Plus X', 'is_active': False})
    assert patch.status_code == 200
    assert patch.get_json()['data']['name'] == 'Pro Plus X'
    assert patch.get_json()['data']['is_active'] is False

    invalid = client.post('/api/v1/admin/plans', headers=headers, json={'name': 'Missing code'})
    assert invalid.status_code == 400


def test_admin_limits_crud_and_usage_guard_behavior(client, app, monkeypatch):
    monkeypatch.setattr('app.api.v1.analysis_routes.AssetAnalysisService.run_technical_analysis', lambda *a, **k: {'ok': True})

    admin_headers = _admin_headers(client, app, 'admin3@example.com')
    user_email = 'limit-user@example.com'
    user_headers = _user_headers(client, user_email)

    with app.app_context():
        seed_plans()
        user = User.query.filter_by(email=user_email).one()
        free = Plan.query.filter_by(code='free').one()
        user.plan_id = free.id
        db.session.commit()
        plan_id = free.id

    create = client.post('/api/v1/admin/limits', headers=admin_headers, json={
        'plan_id': plan_id,
        'feature_key': 'technical_analysis',
        'daily_quota': 2,
        'enabled': True,
    })
    assert create.status_code in (201, 409)

    list_res = client.get(f'/api/v1/admin/limits?plan_id={plan_id}', headers=admin_headers)
    assert list_res.status_code == 200
    items = list_res.get_json()['data']['items']
    limit = next(item for item in items if item['feature_key'] == 'technical_analysis')

    ok1 = client.get('/api/v1/analysis/BTCUSDT/technical', headers=user_headers)
    assert ok1.status_code == 200

    disable = client.patch(f"/api/v1/admin/limits/{limit['id']}", headers=admin_headers, json={'enabled': False})
    assert disable.status_code == 200

    blocked = client.get('/api/v1/analysis/BTCUSDT/technical', headers=user_headers)
    assert blocked.status_code == 403
    assert blocked.get_json()['error']['code'] == 'feature_disabled'

    assert client.get('/api/v1/admin/limits').status_code == 401
    assert client.get('/api/v1/admin/limits', headers=_user_headers(client, 'user4@example.com')).status_code == 403
