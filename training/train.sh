#!/usr/bin/env bash
# KALKAN · Adım 7 · eğitim başlatıcı                                   v1 · 2026-11-21
# Kullanım: bash training/train.sh [yaml]      (varsayılan training/lora.yaml)
set -euo pipefail
cd "$(dirname "$0")/.."
YAML="${1:-training/lora.yaml}"
PY=".spike/venv-mlx/bin/python"
AD=$(grep '^adapter_path' "$YAML" | sed 's/.*"\(.*\)".*/\1/' | xargs basename)
mkdir -p training/logs
[[ -s data/sft/train.jsonl ]] || { echo "Önce: make sft-veri"; exit 1; }
echo "▶ mlx-lm $($PY -c 'import mlx_lm;print(mlx_lm.__version__)') · $YAML → training/logs/$AD.log"
if $PY -m mlx_lm lora --help >/dev/null 2>&1; then CMD=($PY -m mlx_lm lora); else CMD=($PY -m mlx_lm.lora); fi
"${CMD[@]}" -c "$YAML" 2>&1 | tee "training/logs/$AD.log"
cp "$YAML" "training/adapters/$AD/kalkan_lora.yaml"
echo "✔ adapter: training/adapters/$AD · log: training/logs/$AD.log → make loss"
