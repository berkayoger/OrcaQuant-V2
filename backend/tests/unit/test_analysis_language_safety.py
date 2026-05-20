import json

from app.extensions import db
from app.models.plan import Plan
from app.models.user import User
from app.services.plans.seed_plans import seed_plans


FORBIDDEN_TERMS = [
    "guaranteed",
    "guarantee",
    "guaranteed profit",
    "kesin",
    "kesin kazanç",
    "garanti kazanç",
    "risksiz kazanç",
]


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


def _assert_no_forbidden_terms(payload: dict):
    text = json.dumps(payload, ensure_ascii=False).lower()
    for term in FORBIDDEN_TERMS:
        assert term not in text


def test_analysis_endpoints_avoid_dangerous_financial_promises(client, app):
    client.post('/api/v1/assets/sync-sample')
    email = 'analysis-language-safety@example.com'
    headers = _auth_headers(client, email)
    _enable_feature_for_user(app, email)

    technical = client.get('/api/v1/analysis/BTC/technical?timeframe=1d&limit=120', headers=headers)
    assert technical.status_code == 200
    _assert_no_forbidden_terms(technical.get_json())

    scenario = client.post('/api/v1/analysis/BTC/scenario-risk', headers=headers, json={'timeframe': '1d', 'limit': 120, 'horizon_days': 14, 'targets': [{'name': 'target_up', 'direction': 'above', 'price': 30000}]})
    assert scenario.status_code == 200
    _assert_no_forbidden_terms(scenario.get_json())

    full = client.post('/api/v1/analysis/BTC/full', headers=headers, json={'timeframe': '1d', 'limit': 120, 'horizon_days': 14, 'targets': [{'name': 'target_up', 'direction': 'above', 'price': 30000}]})
    assert full.status_code == 200
    _assert_no_forbidden_terms(full.get_json())
