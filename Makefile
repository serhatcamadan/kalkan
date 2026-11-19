# KALKAN v1 · 2026-11-18
.PHONY: spike bench test lint clean-spike
spike:          ## Mac: Adım 1 dönüşüm spike'ı
	bash training/spike/spike_convert.sh
bench:          ## VPS: Ollama benchmark
	bash deploy/bench_vps.sh
test:
	python -m pytest -q
lint:
	ruff check .
clean-spike:    ## spike çıktıları + Ollama'daki spike modelleri
	-ollama rm kalkan-spike-c kalkan-spike-a kalkan-spike-b kalkan-spike-d0
	rm -rf .spike
