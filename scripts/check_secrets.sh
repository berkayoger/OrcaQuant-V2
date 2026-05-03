#!/usr/bin/env bash
set -euo pipefail
if command -v rg >/dev/null; then
  ! rg -n "(AKIA|BEGIN RSA PRIVATE KEY|SECRET_KEY=.{20,})" .
fi
