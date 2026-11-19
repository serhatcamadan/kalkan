#!/usr/bin/env bash
# =============================================================================
# KALKAN · Adım 1 · DÖNÜŞÜM SPIKE'I                       v1.1 · 2026-11-18
# v1.1: Modelfile göreli yol kullanır (klasör adında boşluk olabilir: "AI Engineer")
# 🧪 KESİN DENE (Apple Silicon Mac)
#
# Amaç: Fine-tune'dan Ollama'ya giden yolun UÇTAN UCA çalıştığını, gerçek eğitime
# başlamadan ÖNCE kanıtlamak. 1 iterasyonluk LoRA yeterli: kalite değil, boru hattı.
#
# Üç yol paralel denenir, her biri ayrı log + durum satırı üretir:
#   C (kontrol) : HF bf16 taban ─────────────────────────────► GGUF ► Q4_K_M ► Ollama
#   A (MLX)     : taban ► mlx LoRA ► mlx_lm.fuse ────────────► GGUF ► Q4_K_M ► Ollama
#   B (yedek)   : taban ► mlx LoRA ► adaptörü HF ağırlıklarına
#                 kendi script'imizle birleştir ─────────────► GGUF ► Q4_K_M ► Ollama
# Ayrıca D0: yol haritasındaki `ollama create -q q4_K_M` gerçekten çalışıyor mu?
#
# Kullanım:  bash training/spike/spike_convert.sh
# Ayarlar (ortam değişkeni):
#   MODEL_ID=Qwen/Qwen3.5-0.8B  MODEL_REV=main  MLX_LM_VERSION=0.32.2
#   LLAMA_CPP_REF=master  PY=python3.12  WORK=<repo>/.spike
# Sonuç: $WORK/status.tsv, $WORK/versions.lock, $WORK/smoke.json, $WORK/logs/*
# =============================================================================
set -uo pipefail   # -e YOK: bir yol düşerse diğerleri devam etsin

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
HERE="$ROOT/training/spike"
WORK="${WORK:-$ROOT/.spike}"
MODEL_ID="${MODEL_ID:-Qwen/Qwen3.5-0.8B}"
MODEL_REV="${MODEL_REV:-main}"
MLX_LM_VERSION="${MLX_LM_VERSION:-0.32.2}"
LLAMA_CPP_REF="${LLAMA_CPP_REF:-master}"
PY="${PY:-python3.12}"

mkdir -p "$WORK"/{logs,gguf,ollama}
STATUS="$WORK/status.tsv"; LOCK="$WORK/versions.lock"
: > "$STATUS"; : > "$LOCK"
VMLX="$WORK/venv-mlx"; VLCP="$WORK/venv-llamacpp"; LCP="$WORK/llama.cpp"

say()  { printf '\n\033[1;36m▶ %s\033[0m\n' "$*"; }
lock() { printf '%s=%s\n' "$1" "$2" | tee -a "$LOCK"; }
# step <ad> <komut...>  → çıktı logs/<ad>.log, sonuç status.tsv, süre saniye
step() {
  local name="$1"; shift
  local t0=$SECONDS
  say "$name"
  if "$@" > "$WORK/logs/$name.log" 2>&1; then
    printf '%s\tOK\t%ss\n' "$name" "$((SECONDS-t0))" | tee -a "$STATUS"; return 0
  else
    printf '%s\tFAIL\t%ss\t(son satırlar aşağıda)\n' "$name" "$((SECONDS-t0))" | tee -a "$STATUS"
    tail -n 15 "$WORK/logs/$name.log" | sed 's/^/    │ /'; return 1
  fi
}
ok() { grep -q "^$1"$'\t'"OK" "$STATUS"; }

# ---------------------------------------------------------------- 0. ön koşullar
say "0. Ön koşullar"
[[ "$(uname -s)" == "Darwin" && "$(uname -m)" == "arm64" ]] || { echo "MLX için Apple Silicon Mac gerekli."; exit 1; }
for bin in git cmake ollama "$PY"; do
  command -v "$bin" >/dev/null || { echo "Eksik: $bin  (brew install git cmake ollama python@3.12)"; exit 1; }
done
curl -sf http://127.0.0.1:11434/api/version >/dev/null || { echo "Ollama sunucusu kapalı: 'ollama serve' veya uygulamayı aç."; exit 1; }
lock date "$(date -u +%FT%TZ)"
lock macos "$(sw_vers -productVersion)"
lock chip "$(sysctl -n machdep.cpu.brand_string)"
lock ram_gb "$(( $(sysctl -n hw.memsize) / 1024**3 ))"
lock ollama "$(ollama --version 2>&1 | tail -1)"

# ---------------------------------------------------------------- 1. ortamlar
setup_mlx() {
  "$PY" -m venv "$VMLX" && "$VMLX/bin/pip" install -U pip &&
  "$VMLX/bin/pip" install "mlx-lm==$MLX_LM_VERSION" "huggingface_hub[cli]"
}
setup_llamacpp() {
  { [[ -d "$LCP/.git" ]] || git clone https://github.com/ggml-org/llama.cpp "$LCP"; } &&
  git -C "$LCP" fetch --all --tags && git -C "$LCP" checkout "$LLAMA_CPP_REF" &&
  { [[ "$LLAMA_CPP_REF" != "master" ]] || git -C "$LCP" pull --ff-only; } &&
  cmake -S "$LCP" -B "$LCP/build" -DCMAKE_BUILD_TYPE=Release -DLLAMA_CURL=OFF -DLLAMA_BUILD_TESTS=OFF &&
  cmake --build "$LCP/build" --config Release -j --target llama-quantize llama-cli &&
  "$PY" -m venv "$VLCP" && "$VLCP/bin/pip" install -U pip &&
  "$VLCP/bin/pip" install -r "$LCP/requirements/requirements-convert_hf_to_gguf.txt" &&
  "$VLCP/bin/pip" install safetensors
}
step 1a_setup_mlx setup_mlx || exit 1
step 1b_setup_llamacpp setup_llamacpp || exit 1
lock mlx_lm "$("$VMLX/bin/python" -c 'import mlx_lm;print(mlx_lm.__version__)')"
lock mlx "$("$VMLX/bin/python" -c 'import mlx.core as m;print(m.__version__)')"
lock llama_cpp_commit "$(git -C "$LCP" rev-parse --short HEAD) ($(git -C "$LCP" describe --tags --always))"
lock transformers_convert "$("$VLCP/bin/python" -c 'import transformers;print(transformers.__version__)')"

# mlx-lm CLI biçimi: yeni sürümlerde `python -m mlx_lm lora`, eskilerde `python -m mlx_lm.lora`
if "$VMLX/bin/python" -m mlx_lm lora --help >/dev/null 2>&1; then
  mlx() { local s=$1; shift; "$VMLX/bin/python" -m mlx_lm "$s" "$@"; }
else
  mlx() { local s=$1; shift; "$VMLX/bin/python" -m "mlx_lm.$s" "$@"; }
fi

# ---------------------------------------------------------------- 2. taban model
download() {
  "$VMLX/bin/hf" download "$MODEL_ID" --revision "$MODEL_REV" --local-dir "$WORK/base"
}
step 2_download download || exit 1
lock model "$MODEL_ID"
lock model_sha "$("$VMLX/bin/python" -c "from huggingface_hub import HfApi;print(HfApi().model_info('$MODEL_ID',revision='$MODEL_REV').sha)")"
lock base_dtype "$("$VMLX/bin/python" -c "import json;c=json.load(open('$WORK/base/config.json'));print(c.get('torch_dtype') or c.get('dtype') or c.get('text_config',{}).get('dtype'))")"
lock base_archs "$("$VMLX/bin/python" -c "import json;c=json.load(open('$WORK/base/config.json'));print(c.get('architectures'), c.get('model_type'))")"

# ---------------------------------------------------------------- 3. 1 iterasyon LoRA
step 3a_data "$VMLX/bin/python" "$HERE/make_spike_data.py" "$WORK/data"
train() {
  mlx lora --model "$WORK/base" --train --data "$WORK/data" \
    --iters 1 --batch-size 1 --num-layers 4 --learning-rate 1e-4 \
    --max-seq-length 512 --steps-per-report 1 --val-batches 1 \
    --adapter-path "$WORK/adapters"
}
step 3b_lora_1iter train
step 3c_mlx_generate_with_adapter mlx generate --model "$WORK/base" --adapter-path "$WORK/adapters" \
  --prompt "Merhaba, kısaca kendini tanıt." --max-tokens 40

# ---------------------------------------------------------------- 4. yollar
# A: mlx_lm.fuse çıktısı (taban zaten bf16 → --dequantize gerekmez)
fuse_a() {
  mlx fuse --model "$WORK/base" --adapter-path "$WORK/adapters" --save-path "$WORK/fused_mlx" &&
  # fuse bazı tokenizer/processor dosyalarını taşımayabilir → eksikleri tabandan kopyala (üzerine yazma)
  for f in "$WORK"/base/*.json "$WORK"/base/*.jinja "$WORK"/base/*.txt "$WORK"/base/merges.txt; do
    [[ -e "$f" ]] && [[ "$(basename "$f")" != "config.json" ]] && [[ "$(basename "$f")" != *.safetensors.index.json ]] &&
      cp -n "$f" "$WORK/fused_mlx/" 2>/dev/null; true
  done
}
# B: adaptörü HF isimlendirmesiyle orijinal ağırlıklara biz birleştiririz
merge_b() { "$VLCP/bin/python" "$HERE/merge_mlx_adapter_hf.py" --base "$WORK/base" --adapter "$WORK/adapters" --out "$WORK/merged_hf"; }

ok 3b_lora_1iter && step 4a_fuse_mlx fuse_a
ok 3b_lora_1iter && step 4b_merge_hf merge_b
# Teşhis: taban ↔ A ve taban ↔ B ağırlık farkları (isim, şekil, norm kayması)
ok 4a_fuse_mlx && step 4c_inspect_A "$VLCP/bin/python" "$HERE/inspect_weights.py" "$WORK/base" "$WORK/fused_mlx" --json "$WORK/inspect_A.json"
ok 4b_merge_hf && step 4d_inspect_B "$VLCP/bin/python" "$HERE/inspect_weights.py" "$WORK/base" "$WORK/merged_hf" --json "$WORK/inspect_B.json"

# ---------------------------------------------------------------- 5. GGUF + Q4_K_M
to_gguf() {  # <ad> <kaynak_klasör>
  "$VLCP/bin/python" "$LCP/convert_hf_to_gguf.py" "$2" --outtype bf16 --outfile "$WORK/gguf/$1-BF16.gguf" &&
  "$LCP/build/bin/llama-quantize" "$WORK/gguf/$1-BF16.gguf" "$WORK/gguf/$1-Q4_K_M.gguf" Q4_K_M
}
step 5c_gguf_C to_gguf C "$WORK/base"
ok 4a_fuse_mlx  && step 5a_gguf_A to_gguf A "$WORK/fused_mlx"
ok 4b_merge_hf  && step 5b_gguf_B to_gguf B "$WORK/merged_hf"

# ---------------------------------------------------------------- 6. Ollama
mk_ollama() {  # <ad>   Modelfile GGUF'un yanına yazılır, FROM göreli → boşluklu yol sorunu yok
  ( cd "$WORK/gguf" &&
    printf 'FROM ./%s-Q4_K_M.gguf\nPARAMETER temperature 0\nPARAMETER num_ctx 4096\n' "$1" > "Modelfile.$1" &&
    ollama create "kalkan-spike-$(echo "$1" | tr 'A-Z' 'a-z')" -f "Modelfile.$1" )
}
# D0: yol haritasındaki orijinal plan — BF16 GGUF'tan Ollama içinde kuantize
d0() {
  ( cd "$WORK/gguf" && printf 'FROM ./C-BF16.gguf\n' > Modelfile.D0 &&
    ollama create -q q4_K_M kalkan-spike-d0 -f Modelfile.D0 )
}
MODELS=()
ok 5c_gguf_C && step 6c_ollama_C mk_ollama C && MODELS+=(kalkan-spike-c)
ok 5a_gguf_A && step 6a_ollama_A mk_ollama A && MODELS+=(kalkan-spike-a)
ok 5b_gguf_B && step 6b_ollama_B mk_ollama B && MODELS+=(kalkan-spike-b)
ok 5c_gguf_C && step 6d_ollama_create_q_D0 d0

# ---------------------------------------------------------------- 7. cevap testi
if ((${#MODELS[@]})); then
  step 7_smoke "$VLCP/bin/python" "$HERE/ollama_smoke.py" --out "$WORK/smoke.json" "${MODELS[@]}"
  cat "$WORK/logs/7_smoke.log"
fi

# ---------------------------------------------------------------- özet
say "ÖZET"
column -t -s $'\t' "$STATUS"
echo; echo "Boyutlar:"; ls -lh "$WORK"/gguf/*.gguf 2>/dev/null | awk '{print "  "$5"\t"$9}'
echo; echo "Sürümler → $LOCK"; cat "$LOCK"
cat <<'TXT'

Sonraki adım: .spike/status.tsv, .spike/smoke.json ve .spike/inspect_*.json'u
docs/spike-01-donusum.md'deki tabloya işle ve bu çıktıları sohbete yapıştır.
TXT
