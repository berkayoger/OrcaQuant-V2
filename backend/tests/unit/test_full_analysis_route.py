from app.extensions import db
from app.models.plan import Plan
from app.models.user import User
from app.services.plans.seed_plans import seed_plans


def _auth_headers(client, email: str):
    reg = client.post('/api/v1/auth/register', json={'email': email, 'password': 'Password123'}).get_json()
    return {'Authorization': f"Bearer {reg['access_token']}"}


def _enable_feature_for_user(app, email: str):
    with app.app_context():
        seed_plans()
        user = User.query.filter_by(email=email).one()
        free = Plan.query.filter_by(code='free').one()
        user.plan_id = free.id
        db.session.commit()


def test_full_analysis_route_returns_consensus(client, app):
    client.post('/api/v1/assets/sync-sample')
    email = 'full-analysis@example.com'
    headers = _auth_headers(client, email)
    _enable_feature_for_user(app, email)
    response = client.post('/api/v1/analysis/BTC/full', headers=headers, json={'timeframe': '1d', 'limit': 120, 'horizon_days': 14, 'targets': [{'name': 'target_up', 'direction': 'above', 'price': 30000}]})
    assert response.status_code == 200


def test_full_analysis_route_validates_inputs(client, app):
    client.post('/api/v1/assets/sync-sample')
    email = 'full-analysis-validate@example.com'
    headers = _auth_headers(client, email)
    _enable_feature_for_user(app, email)
    assert client.post('/api/v1/analysis/BTC/full', headers=headers, json={'limit': 49}).status_code == 400
    assert client.post('/api/v1/analysis/BTC/full', headers=headers, json={'horizon_days': 366}).status_code == 400
    assert client.post('/api/v1/analysis/BTC/full', headers=headers, json={'targets': [{'name': 'x', 'direction': 'sideways', 'price': 1}]}).status_code == 400
