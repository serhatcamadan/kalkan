#!/usr/bin/env bash
# KALKAN · Adım 8 · fine-tune adaptörü → GGUF (B yolu, ADR-0001)            v1 · 2026-11-21
# 🧪 KESİN DENE (Mac).  make export-ft   (varsayılan: training/adapters/ft-0.8b-v2-it600 → kalkan-0.8b-v2)
#
# 1) merge_mlx_adapter_hf.py --dtype float32 : orijinal HF düzeni + LoRA farkı, bf16'ya geri yuvarlamadan
# 2) convert_hf_to_gguf.py --outtype f32     : tek ara dosya (~3 GB, sonunda silinir)
# 3) llama-quantize → Q4_K_M (dağıtım) ve Q8_0 (tanı: Q4 paritesi bozuksa suç nicemlemede mi?)
# Spike ile AYNI llama.cpp commit'i ve venv'ler (.spike/venv-llamacpp, .spike/llama.cpp).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="$ROOT/.spike"; LCP="$WORK/llama.cpp"; VLCP="$WORK/venv-llamacpp"
ADP="${1:-training/adapters/ft-0.8b-v2-it600}"; AD="${2:-kalkan-0.8b-v2}"
cd "$ROOT"
[[ -x "$LCP/build/bin/llama-quantize" ]] || { echo "Önce 'make spike' çalışmış olmalı."; exit 1; }
[[ -f "$ADP/adapters.safetensors" && -f "$ADP/adapter_config.json" ]] || { echo "$ADP içinde adaptör yok (make kontrol-08-it ...)"; exit 1; }
MERGED="$WORK/merged_$AD"; mkdir -p "$WORK/gguf"

echo "▶ 1/3 birleştirme (f32): $ADP + .spike/base → $MERGED"
"$VLCP/bin/python" training/spike/merge_mlx_adapter_hf.py --base "$WORK/base" --adapter "$ADP" --out "$MERGED" --dtype float32

echo "▶ 2/3 GGUF F32"
"$VLCP/bin/python" "$LCP/convert_hf_to_gguf.py" "$MERGED" --outtype f32 --outfile "$WORK/gguf/$AD-F32.gguf"

echo "▶ 3/3 nicemleme"
for Q in Q4_K_M Q8_0; do
  "$LCP/build/bin/llama-quantize" "$WORK/gguf/$AD-F32.gguf" "$WORK/gguf/$AD-$Q.gguf" "$Q" >/dev/null 2>&1 \
    || { echo "llama-quantize $Q başarısız"; exit 1; }
done
rm -rf "$WORK/gguf/$AD-F32.gguf" "$MERGED"   # ~6 GB; gerekirse yeniden üretilir

for Q in Q4_K_M Q8_0; do
  printf 'gguf_%s_%s=%s sha256=%s\n' "$AD" "$Q" "$ADP" "$(shasum -a 256 "$WORK/gguf/$AD-$Q.gguf" | cut -c1-16)" | tee -a "$WORK/versions.lock"
done
ls -lh "$WORK/gguf/$AD-"*.gguf
echo "✔ sonraki: ayrı terminalde  make sunucu-ft Q=Q8_0   → burada  make gguf-parite"
