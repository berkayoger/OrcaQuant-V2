def test_market_cockpit_contract(client):
    response = client.get("/api/v1/dashboard/")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["module"] == "market_cockpit"
    assert payload["investment_advice"] is False
    assert payload["market_overview"]["regime"] in {"risk_on", "mixed", "risk_off"}
    assert len(payload["assets"]) == 5
    assert len(payload["radar"]) == 5

    first_asset = payload["assets"][0]
    assert {"symbol", "opportunity_score", "risk_score", "advantages", "risks", "plain_language_summary"}.issubset(first_asset.keys())
    assert first_asset["advantages"]
    assert first_asset["risks"]


def test_orca_radar_contract(client):
    response = client.get("/api/v1/dashboard/radar")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["module"] == "orca_radar"
    assert payload["investment_advice"] is False
    assert len(payload["items"]) == 5
    scores = [item["opportunity_score"] for item in payload["items"]]
    assert scores == sorted(scores, reverse=True)
