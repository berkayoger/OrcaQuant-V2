import pytest

from app.core.errors.exceptions import FeatureLockedError
from app.core.security.feature_gate import has_feature, require_feature


def test_free_plan_missing_scenario_lab() -> None:
    assert has_feature("free", "scenario_lab") is False
    with pytest.raises(FeatureLockedError):
        require_feature("free", "scenario_lab")
