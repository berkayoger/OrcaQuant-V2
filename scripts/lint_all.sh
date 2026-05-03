#!/usr/bin/env bash
set -euo pipefail
[ -f backend/pyproject.toml ] && python -m compileall backend/app
[ -f frontend/package.json ] && (cd frontend && npm run typecheck)
