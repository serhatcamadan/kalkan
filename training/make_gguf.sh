#!/usr/bin/env bash
# KALKAN · HF modeli → GGUF Q4_K_M                                  v1 · 2026-11-19
# 🧪 KESİN DENE (Mac). Spike'ın kurduğu .spike/venv-* ve .spike/llama.cpp'yi kullanır,
# yani dönüşüm Ollama'dan bağımsız ve spike ile AYNI llama.cpp commit'i (ADR-0001/0002).
#
# Kullanım:  bash training/make_gguf.sh <hf_model_id> <kısa_ad>
#   örn.     bash training/make_gguf.sh Qwen/Qwen3.5-2B C2B   → .spike/gguf/C2B-Q4_K_M.gguf
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORK="${WORK:-$ROOT/.spike}"
ID="${1:?hf model id gerekli}"; AD="${2:?kısa ad gerekli}"; REV="${MODEL_REV:-main}"
LCP="$WORK/llama.cpp"; VLCP="$WORK/venv-llamacpp"; VMLX="$WORK/venv-mlx"
[[ -x "$LCP/build/bin/llama-quantize" ]] || { echo "Önce 'make spike' çalışmış olmalı."; exit 1; }

DIR="$WORK/models/$AD"
echo "▶ indiriliyor: $ID@$REV → $DIR"
"$VMLX/bin/hf" download "$ID" --revision "$REV" --local-dir "$DIR"
SHA="$("$VMLX/bin/python" -c "from huggingface_hub import HfApi;print(HfApi().model_info('$ID',revision='$REV').sha)")"

echo "▶ GGUF (bf16) → Q4_K_M"
"$VLCP/bin/python" "$LCP/convert_hf_to_gguf.py" "$DIR" --outtype bf16 --outfile "$WORK/gguf/$AD-BF16.gguf"
"$LCP/build/bin/llama-quantize" "$WORK/gguf/$AD-BF16.gguf" "$WORK/gguf/$AD-Q4_K_M.gguf" Q4_K_M
rm -f "$WORK/gguf/$AD-BF16.gguf"   # yer kazanmak için; gerekirse yeniden üretilir

echo "▶ hızlı cevap testi"
"$LCP/build/bin/llama-cli" -m "$WORK/gguf/$AD-Q4_K_M.gguf" \
  -p "Türkiye'nin başkenti neresidir? Tek cümleyle cevap ver." \
  -n 40 --temp 0 --single-turn --no-display-prompt --reasoning off 2>/dev/null | tail -n 4

printf 'gguf_%s=%s@%s sha256=%s\n' "$AD" "$ID" "$SHA" \
  "$(shasum -a 256 "$WORK/gguf/$AD-Q4_K_M.gguf" | cut -c1-16)" | tee -a "$WORK/versions.lock"
ls -lh "$WORK/gguf/$AD-Q4_K_M.gguf"
