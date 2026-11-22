#!/usr/bin/env bash
# KALKAN · VPS benchmark başlatıcı                                v2.2 · 2026-11-22
# v2.2: bench_vps.py --istem kisa + uretim/uretim_cachesiz senaryoları (384 token, üretimle aynı)
# v2.1: python3 -u → çıktı tee ile anında ekrana düşer (v2 tamponluyordu)
# 🧪 KESİN DENE — temiz Ubuntu 24.04 VPS'te.
# v2: Ollama yerine llama.cpp'nin llama-server'ı (ADR-0002). Mac'teki spike ile AYNI commit derlenir.
#
# Ön koşul: models/ klasöründe GGUF dosyaları (Mac'ten scp ile kopyalanır).
# Kullanım:  bash bench_vps.sh [bench_vps.py argümanları]
set -euo pipefail
cd "$(dirname "$0")"
LLAMA_CPP_COMMIT="${LLAMA_CPP_COMMIT:-5812201a8}"   # Mac spike'ındaki versions.lock ile aynı

ls models/*.gguf >/dev/null 2>&1 || { echo "models/ içinde .gguf yok. Önce Mac'ten kopyala (rehbere bak)."; exit 1; }

# 1) derleme araçları (yalnızca eksikse kurulur)
need=()
for b in git cmake g++ python3; do command -v "$b" >/dev/null || need+=("$b"); done
if ((${#need[@]})); then
  echo "▶ Eksik araçlar kuruluyor: ${need[*]}"
  apt-get update && apt-get install -y build-essential cmake git python3
fi

# 2) llama.cpp — sabit commit, bu CPU için yerel optimizasyon (AVX2) ile
if [[ ! -x llama.cpp/build/bin/llama-server ]]; then
  echo "▶ llama.cpp $LLAMA_CPP_COMMIT derleniyor (4 vCPU'da ~5–15 dk)"
  [[ -d llama.cpp/.git ]] || git clone https://github.com/ggml-org/llama.cpp llama.cpp
  git -C llama.cpp fetch --all --tags
  git -C llama.cpp checkout "$LLAMA_CPP_COMMIT"
  cmake -S llama.cpp -B llama.cpp/build -DCMAKE_BUILD_TYPE=Release -DGGML_NATIVE=ON \
        -DLLAMA_CURL=OFF -DLLAMA_BUILD_TESTS=OFF
  cmake --build llama.cpp/build --config Release -j "$(nproc)" --target llama-server
fi
llama.cpp/build/bin/llama-server --version 2>&1 | tail -2

# 3) benchmark (başka yük olmamalı)
mkdir -p results
python3 -u bench_vps.py "$@" 2>&1 | tee "results/bench-$(date +%Y%m%d-%H%M%S).log"
