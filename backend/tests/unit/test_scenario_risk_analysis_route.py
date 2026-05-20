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


def test_scenario_risk_route_returns_200(client, app):
    client.post('/api/v1/assets/sync-sample')
    email = 'scenario-risk@example.com'
    headers = _auth_headers(client, email)
    _enable_feature_for_user(app, email)
    response = client.post('/api/v1/analysis/BTC/scenario-risk', headers=headers, json={'timeframe': '1d', 'limit': 120, 'horizon_days': 14, 'targets': [{'name': 'target_up', 'direction': 'above', 'price': 30000}]})
    assert response.status_code == 200
