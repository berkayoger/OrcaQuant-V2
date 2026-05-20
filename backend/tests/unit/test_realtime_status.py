def test_realtime_status_disabled_when_flag_off(client):
    res = client.get('/api/v1/market/realtime/status')
    assert res.status_code == 200
    assert res.get_json()['enabled'] is False
    assert res.get_json()['status'] == 'disabled'


def test_realtime_status_not_implemented_when_enabled(client, app):
    app.config['ENABLE_REALTIME'] = True
    res = client.get('/api/v1/market/realtime/status')
    assert res.status_code == 200
    assert res.get_json()['enabled'] is True
    assert res.get_json()['status'] == 'enabled'


def _auth_headers(client, email: str = 'stream@example.com'):
    token = client.post('/api/v1/auth/register', json={'email': email, 'password': 'Password123'}).get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}


def test_realtime_stream_unauthorized(client, app):
    app.config['ENABLE_REALTIME'] = True
    res = client.get('/api/v1/market/realtime/stream/BTC')
    assert res.status_code == 401


def test_realtime_stream_disabled_by_default(client):
    headers = _auth_headers(client, email='stream-disabled@example.com')
    res = client.get('/api/v1/market/realtime/stream/BTC', headers=headers)
    assert res.status_code == 503
    assert res.get_json()['error']['code'] == 'realtime_disabled'


def test_realtime_stream_basic_behavior(client, app):
    app.config['ENABLE_REALTIME'] = True
    headers = _auth_headers(client, email='stream-basic@example.com')

    res = client.get('/api/v1/market/realtime/stream/BTC', headers=headers, buffered=False)
    assert res.status_code == 200
    assert res.headers['Content-Type'].startswith('text/event-stream')
    assert res.headers['X-Realtime-Transport'] == 'sse'

    chunks = list(res.response)
    payload = b''.join(chunks).decode()
    assert 'event: connected' in payload
    assert 'event: heartbeat' in payload
