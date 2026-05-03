#!/usr/bin/env bash
set -euo pipefail

find . -type f | sort

critical_paths=(
  "backend/app/factory.py"
  "backend/app/api/route_registry.py"
  "backend/app/api/v1/auth_routes.py"
  "backend/app/api/v1/analysis_routes.py"
  "backend/app/core/engines/technical_signal_engine.py"
  "backend/app/repositories/analysis_repository.py"
  "backend/app/services/analysis/asset_analysis_service.py"
  "backend/tests/unit/test_technical_signal_engine.py"
  "backend/tests/unit/test_analysis_routes.py"
  "docs/TECHNICAL_ANALYSIS.md"
  "backend/app/core/engines/decision_system.py"
  "backend/app/core/security/feature_gate.py"
  "backend/app/services/billing/plan_service.py"
  "backend/app/services/limits/usage_meter_service.py"
  "backend/app/models/user.py"
  "backend/app/models/plan.py"
  "backend/app/models/usage_event.py"
  "backend/app/repositories/user_repository.py"
  "backend/migrations/env.py"
  "backend/tests/unit/test_user_repository.py"
  "backend/app/services/market_data/sample_provider.py"
  "backend/app/repositories/asset_repository.py"
  "backend/app/repositories/market_data_repository.py"
  "backend/app/seeds/seed_assets.py"
  "docs/MARKET_DATA.md"
  "backend/tests/unit/test_market_routes.py"
  "frontend/package.json"
  "frontend/src/app/router.tsx"
  "frontend/src/features/auth/api.ts"
  "frontend/src/features/analysis/api.ts"
  "docs/SECURITY_MODEL.md"
  ".github/workflows/backend-ci.yml"
)

for path in "${critical_paths[@]}"; do
  if [[ ! -e "$path" ]]; then
    echo "Missing required path: $path" >&2
    exit 1
  fi
done

echo "Critical path validation passed."
