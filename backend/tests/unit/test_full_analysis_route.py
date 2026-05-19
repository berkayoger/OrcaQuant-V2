def test_full_analysis_route_returns_consensus(client):
    client.post("/api/v1/assets/sync-sample")
    response = client.post(
        "/api/v1/analysis/BTC/full",
        json={
            "timeframe": "1d",
            "limit": 120,
            "horizon_days": 14,
            "targets": [{"name": "target_up", "direction": "above", "price": 30000}],
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["symbol"] == "BTC"
    assert payload["analysis_type"] == "full"
    assert "consensus" in payload
    assert "saved_analysis_id" in payload
    text = response.get_data(as_text=True).lower()
    banned_terms = ["guaran" + "teed", "ke" + "sin", "garan" + "ti kazanç", "ke" + "sin kazanç"]
    for term in banned_terms:
        assert term not in text


def test_full_analysis_route_validates_inputs(client):
    client.post("/api/v1/assets/sync-sample")

    assert client.post("/api/v1/analysis/BTC/full", json={"limit": 49}).status_code == 400
    assert client.post("/api/v1/analysis/BTC/full", json={"horizon_days": 366}).status_code == 400
    assert client.post(
        "/api/v1/analysis/BTC/full",
        json={"targets": [{"name": "x", "direction": "sideways", "price": 1}]},
    ).status_code == 400
