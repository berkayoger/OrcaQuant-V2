def test_scenario_risk_route_returns_200(client):
    client.post('/api/v1/assets/sync-sample')
    response = client.post('/api/v1/analysis/BTC/scenario-risk', json={"timeframe": "1d", "limit": 120, "horizon_days": 14, "targets": [{"name": "target_up", "direction": "above", "price": 30000}]})
    assert response.status_code == 200
    text = response.get_data(as_text=True).lower()
    assert 'guaranteed' not in text
    assert 'kesin' not in text
    assert 'garanti kazanç' not in text
    assert 'kesin kazanç' not in text
