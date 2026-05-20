
def _register_and_access(client, email='bill@example.com'):
    return client.post('/api/v1/auth/register', json={'email': email, 'password': 'Password123'}).get_json()['access_token']


def test_billing_status_disabled_by_default(client):
    res = client.get('/api/v1/billing/status')
    assert res.status_code == 200
    assert res.get_json()['enabled'] is False
    assert res.get_json()['status'] == 'disabled'


def test_billing_initiate_requires_auth(client):
    res = client.post('/api/v1/billing/initiate', json={})
    assert res.status_code == 401


def test_billing_initiate_returns_billing_disabled_when_flag_off(client):
    token = _register_and_access(client)
    res = client.post('/api/v1/billing/initiate', headers={'Authorization': f'Bearer {token}'}, json={})
    assert res.status_code == 501
    assert res.get_json()['code'] == 'billing_disabled'


def test_billing_initiate_not_implemented_when_enabled(client, app):
    token = _register_and_access(client, 'bill2@example.com')
    app.config['ENABLE_BILLING'] = True
    res = client.post('/api/v1/billing/initiate', headers={'Authorization': f'Bearer {token}'}, json={})
    assert res.status_code == 501
    assert res.get_json()['code'] == 'not_implemented'
