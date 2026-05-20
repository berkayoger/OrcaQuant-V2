def test_docs_status_endpoint_returns_openapi_link(client):
    res = client.get('/api/v1/docs/')
    assert res.status_code == 200
    payload = res.get_json()
    assert payload['status'] == 'ok'
    assert payload['openapi_url'] == '/api/v1/docs/openapi.json'
    assert payload['message'].lower().find('openapi') >= 0


def test_openapi_json_contains_required_top_level_keys(client):
    res = client.get('/api/v1/docs/openapi.json')
    assert res.status_code == 200
    payload = res.get_json()
    assert 'openapi' in payload
    assert 'info' in payload
    assert 'paths' in payload


def test_openapi_json_contains_v2_core_routes(client):
    res = client.get('/api/v1/docs/openapi.json')
    paths = res.get_json()['paths']
    assert '/api/v1/auth/register' in paths
    assert '/api/v1/auth/refresh' in paths
    assert '/api/v1/analysis/full' in paths
    assert '/api/v1/billing/status' in paths
    assert '/api/v1/market/realtime/status' in paths
