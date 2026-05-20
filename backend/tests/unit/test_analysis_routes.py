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


def test_analysis_technical_route_returns_200(client, app):
    client.post('/api/v1/assets/sync-sample')
    email = 'analysis-tech@example.com'
    headers = _auth_headers(client, email)
    _enable_feature_for_user(app, email)
    response = client.get('/api/v1/analysis/BTC/technical?timeframe=1d&limit=120', headers=headers)
    assert response.status_code == 200


def test_analysis_latest_route_returns_404_without_record(client):
    client.post('/api/v1/assets/sync-sample')
    headers = _auth_headers(client, 'analysis-latest@example.com')
    response = client.get('/api/v1/analysis/BTC/latest?analysis_type=technical', headers=headers)
    assert response.status_code == 404
