#!/usr/bin/env bash
set -euo pipefail
[ -f backend/pyproject.toml ] && echo "Use black/isort in CI"
[ -f frontend/package.json ] && echo "Use prettier in CI"
