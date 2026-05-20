# Plan Limits and Usage

Protected analysis features fail closed:
- no plan => `403 plan_required`
- missing plan limit => `403 feature_not_configured`
- disabled/zero quota => `403 feature_disabled`
- exhausted quota => `429 quota_exceeded`

Usage is incremented only after successful protected responses.
