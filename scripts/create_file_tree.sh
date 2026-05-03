#!/usr/bin/env bash
set -euo pipefail

echo "OrcaQuant v2 kapsamlı dosya ağacı bu repoda kademeli olarak üretilecektir."
echo "Bu script yalnızca başlangıç iskeletinin varlığını doğrular."

required=(backend frontend infra docs scripts .github)
for dir in "${required[@]}"; do
  if [[ -d "$dir" ]]; then
    echo "[ok] $dir"
  else
    echo "[missing] $dir"
    exit 1
  fi
done
