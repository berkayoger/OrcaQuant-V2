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
    assert res.get_json()['status'] == 'not_implemented'
