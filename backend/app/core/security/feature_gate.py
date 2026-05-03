"""Feature-gating helpers by plan."""

from app.core.errors.exceptions import FeatureLockedError

PLAN_FEATURES: dict[str, set[str]] = {
    "free": {"basic_analysis"},
    "pro": {"basic_analysis", "scenario_lab", "personal_suitability"},
    "premium": {"basic_analysis", "scenario_lab", "portfolio_engine", "personal_suitability", "admin_panel"},
}


def has_feature(plan: str, feature: str) -> bool:
    return feature in PLAN_FEATURES.get(plan, set())


def require_feature(plan: str, feature: str) -> None:
    if not has_feature(plan, feature):
        raise FeatureLockedError(f"Feature '{feature}' is not available for plan '{plan}'")
