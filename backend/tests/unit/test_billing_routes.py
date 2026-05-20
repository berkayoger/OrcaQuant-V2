from app.models.payment import PaymentTransaction
from app.models.user import User


def _register_and_access(client, email='bill@example.com'):
    payload = client.post('/api/v1/auth/register', json={'email': email, 'password': 'Password123'}).get_json()
    return payload['access_token'], payload['user']['id']


def test_billing_status_disabled_by_default(client):
    res = client.get('/api/v1/billing/status')
    assert res.status_code == 200
    assert res.get_json()['enabled'] is False
    assert res.get_json()['status'] == 'disabled'


def test_billing_initiate_requires_auth(client):
    res = client.post('/api/v1/billing/initiate', json={})
    assert res.status_code == 401


def test_billing_initiate_requires_idempotency_key(client, app):
    token, _ = _register_and_access(client)
    app.config['ENABLE_BILLING'] = True
    res = client.post('/api/v1/billing/initiate', headers={'Authorization': f'Bearer {token}'}, json={'plan_code': 'pro', 'amount': 100})
    assert res.status_code == 400
    assert res.get_json()['code'] == 'missing_idempotency_key'


def test_billing_idempotency_replay_returns_same_transaction(client, app):
    token, user_id = _register_and_access(client, 'bill2@example.com')
    app.config['ENABLE_BILLING'] = True
    headers = {'Authorization': f'Bearer {token}', 'Idempotency-Key': 'idem-1'}

    res1 = client.post('/api/v1/billing/initiate', headers=headers, json={'plan_code': 'pro', 'amount': 100, 'currency': 'TRY'})
    assert res1.status_code == 202
    res2 = client.post('/api/v1/billing/initiate', headers=headers, json={'plan_code': 'pro', 'amount': 100, 'currency': 'TRY'})
    assert res2.status_code == 200
    assert res2.get_json()['idempotent_replay'] is True

    with app.app_context():
        txns = PaymentTransaction.query.filter_by(user_id=user_id).all()
        assert len(txns) == 1
        assert txns[0].status == 'pending'


def test_callback_unverified_does_not_activate_subscription(client, app):
    token, user_id = _register_and_access(client, 'bill3@example.com')
    app.config['ENABLE_BILLING'] = True
    headers = {'Authorization': f'Bearer {token}', 'Idempotency-Key': 'idem-2'}

    client.post('/api/v1/billing/initiate', headers=headers, json={'plan_code': 'pro', 'amount': 100})
    with app.app_context():
        txn = PaymentTransaction.query.filter_by(user_id=user_id).first()

    cb = client.post(
        '/api/v1/billing/callback/iyzico',
        headers={'X-Iyzico-Signature': 'invalid'},
        json={'conversationId': txn.provider_conversation_id, 'paymentStatus': 'paid', 'mock_verified': False},
    )
    assert cb.status_code == 200
    assert cb.get_json()['verified'] is False

    with app.app_context():
        user = User.query.get(user_id)
        assert user.subscription_status == 'free'


def test_callback_mock_verified_can_activate_subscription(client, app):
    token, user_id = _register_and_access(client, 'bill4@example.com')
    app.config['ENABLE_BILLING'] = True
    headers = {'Authorization': f'Bearer {token}', 'Idempotency-Key': 'idem-3'}

    client.post('/api/v1/billing/initiate', headers=headers, json={'plan_code': 'pro', 'amount': 100})
    with app.app_context():
        txn = PaymentTransaction.query.filter_by(user_id=user_id).first()

    cb = client.post(
        '/api/v1/billing/callback/iyzico',
        headers={'X-Iyzico-Signature': 'valid-test-signature'},
        json={'conversationId': txn.provider_conversation_id, 'paymentStatus': 'paid', 'mock_verified': True},
    )
    assert cb.status_code == 200
    assert cb.get_json()['status'] == 'paid'

    with app.app_context():
        user = User.query.get(user_id)
        assert user.subscription_status == 'active'
