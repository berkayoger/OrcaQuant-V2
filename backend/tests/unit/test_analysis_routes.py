def test_analysis_technical_route_returns_200(client):
    client.post('/api/v1/assets/sync-sample')
    response = client.get('/api/v1/analysis/BTC/technical?timeframe=1d&limit=120')
    assert response.status_code == 200
    text = response.get_data(as_text=True).lower()
    assert 'guaranteed' not in text
    assert 'kesin' not in text
    assert 'garanti kazanç' not in text


def test_analysis_latest_route_returns_404_without_record(client):
    client.post('/api/v1/assets/sync-sample')
    response = client.get('/api/v1/analysis/BTC/latest?analysis_type=technical')
    assert response.status_code == 404
