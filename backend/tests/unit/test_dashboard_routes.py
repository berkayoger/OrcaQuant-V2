def _register(client, email: str):
    return client.post("/api/v1/auth/register", json={"email": email, "password": "Password123"}).get_json()


def _auth_headers(client, email: str = "watcher@example.com"):
    token = _register(client, email)["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_market_cockpit_contract(client):
    response = client.get("/api/v1/dashboard/")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["module"] == "market_cockpit"
    assert payload["investment_advice"] is False
    assert payload["market_overview"]["regime"] in {"risk_on", "mixed", "risk_off"}
    assert len(payload["assets"]) == 5
    assert len(payload["radar"]) == 5
    assert payload["suggested_alerts"]

    first_asset = payload["assets"][0]
    assert {"symbol", "opportunity_score", "risk_score", "advantages", "risks", "plain_language_summary", "signals", "suggested_alerts", "data_source"}.issubset(first_asset.keys())
    assert first_asset["advantages"]
    assert first_asset["risks"]
    assert first_asset["signals"]


def test_market_cockpit_accepts_symbol_and_watchlist_filters(client):
    response = client.get("/api/v1/dashboard/?symbols=BTC,SOL&watchlist=SOL")

    assert response.status_code == 200
    payload = response.get_json()
    assert [asset["symbol"] for asset in payload["assets"]] == ["BTC", "SOL"]
    assert [item["symbol"] for item in payload["watchlist_focus"]] == ["SOL"]


def test_orca_radar_contract(client):
    response = client.get("/api/v1/dashboard/radar")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["module"] == "orca_radar"
    assert payload["investment_advice"] is False
    assert len(payload["items"]) == 5
    assert payload["suggested_alerts"]
    scores = [item["opportunity_score"] for item in payload["items"]]
    assert scores == sorted(scores, reverse=True)


def test_watchlist_crud_and_cockpit(client):
    headers = _auth_headers(client)

    empty = client.get("/api/v1/watchlist/", headers=headers)
    assert empty.status_code == 200
    assert empty.get_json()["data"]["symbols"] == []

    replace = client.put("/api/v1/watchlist/", headers=headers, json={"symbols": ["btc", "SOL", "btc"]})
    assert replace.status_code == 200
    assert replace.get_json()["data"]["symbols"] == ["BTC", "SOL"]

    add = client.post("/api/v1/watchlist/symbols", headers=headers, json={"symbol": "eth"})
    assert add.status_code == 200
    assert add.get_json()["data"]["symbols"] == ["BTC", "SOL", "ETH"]

    cockpit = client.get("/api/v1/watchlist/cockpit", headers=headers)
    assert cockpit.status_code == 200
    data = cockpit.get_json()["data"]
    assert data["watchlist_focus"]
    assert {item["symbol"] for item in data["watchlist_focus"]} == {"BTC", "SOL", "ETH"}

    remove = client.delete("/api/v1/watchlist/symbols/SOL", headers=headers)
    assert remove.status_code == 200
    assert remove.get_json()["data"]["symbols"] == ["BTC", "ETH"]


def test_alert_rules_and_suggestions(client):
    headers = _auth_headers(client, "alerts@example.com")

    suggestions = client.get("/api/v1/alerts/suggestions?symbols=BTC,SOL")
    assert suggestions.status_code == 200
    assert suggestions.get_json()["data"]["items"]

    create = client.post(
        "/api/v1/alerts/",
        headers=headers,
        json={"symbol": "btc", "metric": "opportunity_score", "condition": ">=", "threshold": 72},
    )
    assert create.status_code == 201
    rule_id = create.get_json()["data"]["id"]

    list_response = client.get("/api/v1/alerts/", headers=headers)
    assert list_response.status_code == 200
    assert any(item["id"] == rule_id for item in list_response.get_json()["data"]["items"])

    patch = client.patch(f"/api/v1/alerts/{rule_id}", headers=headers, json={"enabled": False})
    assert patch.status_code == 200
    assert patch.get_json()["data"]["enabled"] is False

    delete = client.delete(f"/api/v1/alerts/{rule_id}", headers=headers)
    assert delete.status_code == 200
    assert delete.get_json()["data"]["deleted"] is True


def test_alert_rule_engine_triggers_and_delivers_notification_with_cooldown(client):
    headers = _auth_headers(client, "alert-engine@example.com")

    create = client.post(
        "/api/v1/alerts/",
        headers=headers,
        json={
            "symbol": "btc",
            "metric": "risk_score",
            "condition": "<=",
            "threshold": 100,
            "cooldown_minutes": 60,
            "channels": ["in_app", "email"],
        },
    )
    assert create.status_code == 201
    created_rule = create.get_json()["data"]
    rule_id = created_rule["id"]
    assert created_rule["cooldown_minutes"] == 60
    assert created_rule["channels"] == ["in_app", "email"]

    first_evaluation = client.post(f"/api/v1/alerts/{rule_id}/evaluate", headers=headers)
    assert first_evaluation.status_code == 200
    first_data = first_evaluation.get_json()["data"]
    assert first_data["evaluated"] == 1
    assert first_data["triggered_count"] == 1
    assert first_data["delivered_count"] == 1
    assert first_data["delivery_status"] == "in_app_persisted"
    assert first_data["results"][0]["triggered"] is True
    assert first_data["deliveries"][0]["delivery_status"]["in_app"] == "created"
    assert first_data["deliveries"][0]["delivery_status"]["email"] == "not_configured"

    notifications = client.get("/api/v1/notifications/", headers=headers)
    assert notifications.status_code == 200
    notification_data = notifications.get_json()["data"]
    assert notification_data["unread_count"] == 1
    assert notification_data["items"][0]["type"] == "alert"
    notification_id = notification_data["items"][0]["id"]

    read = client.patch(f"/api/v1/notifications/{notification_id}/read", headers=headers)
    assert read.status_code == 200
    assert read.get_json()["data"]["status"] == "read"

    second_evaluation = client.post("/api/v1/alerts/evaluate", headers=headers)
    assert second_evaluation.status_code == 200
    second_data = second_evaluation.get_json()["data"]
    assert second_data["evaluated"] == 1
    assert second_data["triggered_count"] == 0
    assert second_data["suppressed_count"] == 1
    assert second_data["delivered_count"] == 0
    assert second_data["results"][0]["status"] == "suppressed_by_cooldown"

    list_response = client.get("/api/v1/alerts/", headers=headers)
    assert list_response.status_code == 200
    rule = list_response.get_json()["data"]["items"][0]
    assert rule["trigger_count"] == 1
    assert rule["last_triggered_at"]
    assert rule["last_value"] is not None


def test_daily_brief_notification_center_flow(client):
    headers = _auth_headers(client, "brief@example.com")

    create = client.post("/api/v1/notifications/daily-brief", headers=headers, json={"symbols": ["BTC", "ETH"]})
    assert create.status_code == 200
    payload = create.get_json()["data"]
    assert payload["created"] is True
    assert payload["notification"]["type"] == "daily_brief"
    assert payload["brief"]["module"] == "orca_daily_brief"

    duplicate = client.post("/api/v1/notifications/daily-brief", headers=headers, json={"symbols": ["BTC", "ETH"]})
    assert duplicate.status_code == 200
    assert duplicate.get_json()["data"]["created"] is False

    unread = client.get("/api/v1/notifications/?status=unread", headers=headers)
    assert unread.status_code == 200
    assert unread.get_json()["data"]["unread_count"] == 1

    mark_all = client.patch("/api/v1/notifications/read-all", headers=headers)
    assert mark_all.status_code == 200
    assert mark_all.get_json()["data"]["updated"] == 1


def test_expanded_product_feature_suite_endpoints(client):
    daily = client.get("/api/v1/dashboard/daily-brief?symbols=BTC,ETH,SOL")
    assert daily.status_code == 200
    daily_payload = daily.get_json()
    assert daily_payload["module"] == "orca_daily_brief"
    assert daily_payload["investment_advice"] is False
    assert daily_payload["leaders"]
    assert daily_payload["suggested_alerts"]

    asset = client.get("/api/v1/dashboard/assets/BTC")
    assert asset.status_code == 200
    asset_payload = asset.get_json()
    assert asset_payload["module"] == "asset_detail"
    assert asset_payload["asset"]["symbol"] == "BTC"
    assert asset_payload["quick_actions"]

    radar_v2 = client.get("/api/v1/dashboard/radar/variants?symbols=BTC,ETH,SOL")
    assert radar_v2.status_code == 200
    variants = radar_v2.get_json()["variants"]
    assert {"daily_top_5", "momentum_radar", "risk_radar", "volume_radar", "trend_radar", "pump_risk_watch"}.issubset(variants.keys())

    portfolio = client.post(
        "/api/v1/dashboard/portfolio/assistant",
        json={"holdings": [{"symbol": "BTC", "allocation_pct": 60}, {"symbol": "ETH", "allocation_pct": 40}]},
    )
    assert portfolio.status_code == 200
    portfolio_payload = portfolio.get_json()
    assert portfolio_payload["module"] == "portfolio_assistant"
    assert portfolio_payload["holdings"]
    assert portfolio_payload["insights"]
    assert portfolio_payload["investment_advice"] is False

    plans = client.get("/api/v1/dashboard/plans")
    assert plans.status_code == 200
    assert [plan["key"] for plan in plans.get_json()["plans"]] == ["free", "pro", "premium"]

    suite = client.get("/api/v1/dashboard/features/suite?symbols=BTC,ETH,SOL")
    assert suite.status_code == 200
    suite_payload = suite.get_json()
    assert suite_payload["module"] == "orcaquant_product_suite"
    assert suite_payload["daily_brief"]
    assert suite_payload["radar_v2"]
    assert suite_payload["portfolio_assistant"]
    assert suite_payload["feature_boundaries"]
