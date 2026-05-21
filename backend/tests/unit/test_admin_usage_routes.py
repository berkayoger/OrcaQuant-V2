from app.extensions import db
from app.models.user import User


def _register(client, email: str):
    return client.post('/api/v1/auth/register', json={'email': email, 'password': 'Password123'}).get_json()


def _admin_headers(client, app, email='admin-usage@example.com'):
    token = _register(client, email)['access_token']
    with app.app_context():
        user = User.query.filter_by(email=email).one()
        user.role = 'admin'
        db.session.commit()
    return {'Authorization': f'Bearer {token}'}


def test_admin_usage_crud_contract(client, app):
    admin = _admin_headers(client, app)
    uid = _register(client, 'usage-target@example.com')['user']['id']

    create = client.post('/api/v1/admin/usage', headers=admin, json={'user_id': uid, 'feature_key': 'technical_analysis', 'used_count': 2})
    assert create.status_code == 201
    row_id = create.get_json()['data']['id']

    list_res = client.get(f'/api/v1/admin/usage?user_id={uid}', headers=admin)
    assert list_res.status_code == 200
    items = list_res.get_json()['data']['items']
    assert any(i['id'] == row_id for i in items)


def test_admin_usage_requires_admin(client):
    assert client.get('/api/v1/admin/usage').status_code == 401
    token = _register(client, 'plain-usage@example.com')['access_token']
    assert client.get('/api/v1/admin/usage', headers={'Authorization': f'Bearer {token}'}).status_code == 403
