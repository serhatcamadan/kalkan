#!/usr/bin/env bash
# KALKAN · VPS benchmark başlatıcı                                  v1 · 2026-11-18
# 🧪 KESİN DENE — temiz VPS'te (Ubuntu/Debian), iade süresi içinde.
# Ollama yoksa resmi script ile kurar, servisi başlatır, bench_vps.py'yi çalıştırır.
# Kullanım:  bash deploy/bench_vps.sh [bench_vps.py argümanları]
set -euo pipefail
cd "$(dirname "$0")"

command -v python3 >/dev/null || { sudo apt-get update && sudo apt-get install -y python3; }
if ! command -v ollama >/dev/null; then
  echo "▶ Ollama kuruluyor (https://ollama.com/install.sh)"
  curl -fsSL https://ollama.com/install.sh | sh
fi
if ! curl -sf http://127.0.0.1:11434/api/version >/dev/null; then
  (sudo systemctl start ollama 2>/dev/null) || (nohup ollama serve >/tmp/ollama.log 2>&1 &)
  for _ in $(seq 30); do curl -sf http://127.0.0.1:11434/api/version >/dev/null && break; sleep 1; done
fi
echo "▶ Ollama $(curl -s http://127.0.0.1:11434/api/version)"
# Not: benchmark sırasında başka yük olmamalı; 'top' ile kontrol et.
mkdir -p results
python3 bench_vps.py "$@" 2>&1 | tee "results/bench-$(date +%Y%m%d-%H%M%S).log"
