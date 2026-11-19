# KALKAN v1.3 · 2026-11-19
.PHONY: spike gguf-2b bench-mac bench test lint clean-spike
spike:          ## Mac: Adım 1 dönüşüm spike'ı
	bash training/spike/spike_convert.sh
gguf-2b:        ## Mac: Qwen3.5-2B → .spike/gguf/C2B-Q4_K_M.gguf
	bash training/make_gguf.sh Qwen/Qwen3.5-2B C2B
bench-mac:      ## Mac: llama-server ölçümü (C, B ve varsa C2B)
	@test -x .spike/llama.cpp/build/bin/llama-server || cmake --build .spike/llama.cpp/build --config Release -j --target llama-server
	LLAMA_SERVER=.spike/llama.cpp/build/bin/llama-server python3 deploy/bench_vps.py --no-disk --runs 5 \
	  --models $(wildcard .spike/gguf/*-Q4_K_M.gguf)
bench:          ## VPS: deploy/ klasörünün içinde çalıştır → bash bench_vps.sh
	bash deploy/bench_vps.sh
test:
	python -m pytest -q
lint:
	ruff check .
clean-spike:
	-ollama rm kalkan-spike-c kalkan-spike-a kalkan-spike-b kalkan-spike-d0
	rm -rf .spike
