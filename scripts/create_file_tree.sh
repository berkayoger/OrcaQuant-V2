#!/usr/bin/env bash
set -euo pipefail

find . -type f | sort

critical_paths=(
  "backend/app/factory.py"
  "backend/app/api/route_registry.py"
  "backend/app/api/v1/auth_routes.py"
  "backend/app/api/v1/analysis_routes.py"
  "backend/app/core/engines/decision_system.py"
  "backend/app/core/security/feature_gate.py"
  "backend/app/services/billing/plan_service.py"
  "backend/app/services/limits/usage_meter_service.py"
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
