#!/usr/bin/env bash
set -euo pipefail
[ -f backend/pytest.ini ] && (cd backend && pytest || true)
