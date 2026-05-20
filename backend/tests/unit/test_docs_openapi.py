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
    for name in ('AuthResponse', 'User', 'UsageStatus', 'LimitsStatus', 'TechnicalAnalysisResponse', 'ScenarioRiskResponse', 'FullAnalysisResponse', 'BillingStatus', 'RealtimeStatus', 'ErrorResponse'):
        assert name in schemas


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


def _walk_schema_nodes(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from _walk_schema_nodes(value)
    elif isinstance(node, list):
        for item in node:
            yield from _walk_schema_nodes(item)


def test_openapi_avoids_json_schema_union_syntax_and_unsafe_ref_siblings(client):
    payload = client.get('/api/v1/docs/openapi.json').get_json()
    allowed_ref_siblings = {'$ref', 'description', 'title'}

    for node in _walk_schema_nodes(payload):
        node_type = node.get('type')
        if isinstance(node_type, list):
            raise AssertionError(f'OpenAPI 3.0 schema uses unsupported union type list: {node_type}')

        if '$ref' in node and len(node.keys()) > 1:
            assert set(node.keys()).issubset(allowed_ref_siblings), f'Unsafe $ref sibling keys: {set(node.keys())}'


def test_openapi_limits_status_schema_and_security(client):
    payload = client.get('/api/v1/docs/openapi.json').get_json()
    path_item = payload['paths']['/api/v1/limits/status']['get']
    assert path_item['security'] == [{'BearerAuth': []}]
    assert path_item['responses']['200']['content']['application/json']['schema']['$ref'] == '#/components/schemas/LimitsStatus'

    schema = payload['components']['schemas']['LimitsStatus']
    assert schema['required'] == ['plan_id', 'plan', 'features']
    for field in ('plan_id', 'plan', 'features'):
        assert field in schema['properties']

    plan_prop = schema['properties']['plan']
    assert plan_prop['nullable'] is True
    assert plan_prop['allOf'][0]['$ref'] == '#/components/schemas/LimitsPlan'

    feature_schema = payload['components']['schemas']['LimitsFeatureStatus']
    for field in ('feature_key', 'used', 'quota', 'remaining', 'percent', 'warning_level', 'exhausted'):
        assert field in feature_schema['properties']
    for field in ('feature_key', 'used', 'quota', 'remaining', 'percent', 'warning_level', 'exhausted'):
        assert field in feature_schema['required']
