from app.core.engines.enums import Decision


def test_decision_enum_contains_sprint_one_values():
    values = {decision.value for decision in Decision}

    assert "BUY_CANDIDATE" in values
    assert "WATCH" in values
    assert "AVOID" in values
    assert "HIGH_RISK_OPPORTUNITY" in values
