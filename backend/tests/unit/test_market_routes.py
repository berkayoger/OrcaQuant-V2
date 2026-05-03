def test_market_routes_sync_and_get(client):
    client.post('/api/v1/assets/sync-sample')
    sync_resp = client.post('/api/v1/market/BTC/sync?timeframe=1d&limit=8')
    assert sync_resp.status_code == 200
    data_resp = client.get('/api/v1/market/BTC/ohlcv?timeframe=1d&limit=8')
    assert data_resp.status_code == 200
    assert len(data_resp.get_json()['rows']) == 8
