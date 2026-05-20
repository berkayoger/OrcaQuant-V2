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
    assert 'components' in payload


def test_openapi_json_contains_v2_core_routes(client):
    res = client.get('/api/v1/docs/openapi.json')
    paths = res.get_json()['paths']
    assert '/api/v1/auth/register' in paths
    assert '/api/v1/auth/refresh' in paths
    assert '/api/v1/analysis/{symbol}/technical' in paths
    assert '/api/v1/analysis/{symbol}/latest' in paths
    assert '/api/v1/analysis/{symbol}/scenario-risk' in paths
    assert '/api/v1/analysis/{symbol}/full' in paths
    assert '/api/v1/billing/status' in paths
    assert '/api/v1/market/realtime/status' in paths
    assert '/api/v1/limits/status' in paths


def test_openapi_components_include_security_schemes_and_schemas(client):
    res = client.get('/api/v1/docs/openapi.json')
    components = res.get_json()['components']

    assert 'securitySchemes' in components
    assert 'BearerAuth' in components['securitySchemes']

    schemas = components['schemas']
    assert 'AuthResponse' in schemas
    assert 'User' in schemas
    assert 'UsageStatus' in schemas
    assert 'LimitsStatus' in schemas
    assert 'TechnicalAnalysisResponse' in schemas
    assert 'ScenarioRiskResponse' in schemas
    assert 'FullAnalysisResponse' in schemas
    assert 'BillingStatus' in schemas
    assert 'RealtimeStatus' in schemas
    assert 'ErrorResponse' in schemas


def test_openapi_analysis_paths_document_symbol_param_and_usage_headers(client):
    res = client.get('/api/v1/docs/openapi.json')
    paths = res.get_json()['paths']

    technical = paths['/api/v1/analysis/{symbol}/technical']['get']
    assert technical['parameters'][0]['$ref'] == '#/components/parameters/SymbolParam'
    assert 'headers' in technical['responses']['200']
    assert 'X-Usage-Used' in technical['responses']['200']['headers']
    assert 'X-Usage-Quota' in technical['responses']['200']['headers']
    assert 'X-Usage-Remaining' in technical['responses']['200']['headers']

def test_openapi_paths_match_registered_routes(client, app):
    res = client.get('/api/v1/docs/openapi.json')
    documented_paths = set(res.get_json()['paths'].keys())

    flask_paths = {rule.rule for rule in app.url_map.iter_rules()}
    normalized_flask_paths = {p.replace('<string:symbol>', '{symbol}').replace('<symbol>', '{symbol}') for p in flask_paths}

    for path in documented_paths:
        assert path in normalized_flask_paths

    assert '/api/v1/me/' in documented_paths
    assert '/api/v1/me/usage' in documented_paths


def test_openapi_limits_status_schema_and_security(client):
    res = client.get('/api/v1/docs/openapi.json')
    payload = res.get_json()
    path_item = payload['paths']['/api/v1/limits/status']['get']
    assert path_item['security'] == [{'BearerAuth': []}]
    schema_ref = path_item['responses']['200']['content']['application/json']['schema']['$ref']
    assert schema_ref == '#/components/schemas/LimitsStatus'

    schema = payload['components']['schemas']['LimitsStatus']
    for field in ('plan_id', 'plan', 'features'):
        assert field in schema['properties']

    feature_schema = payload['components']['schemas']['LimitsFeatureStatus']['properties']
    for field in ('feature_key', 'used', 'quota', 'remaining', 'percent', 'warning_level', 'exhausted'):
        assert field in feature_schema
