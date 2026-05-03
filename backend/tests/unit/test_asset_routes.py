def test_asset_routes_sync_and_list(client):
    sync_resp = client.post('/api/v1/assets/sync-sample')
    assert sync_resp.status_code == 200
    resp = client.get('/api/v1/assets')
    assert resp.status_code == 200
    assert len(resp.get_json()['items']) == 5
