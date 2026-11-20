# KALKAN v4.0 · 2026-11-19
.PHONY: eval eval-hizli rapor llm-paket llm-iceri teyit veri veri-istatistik incele golden dis-veri token-olc spike gguf-2b bench-mac bench test lint clean-spike
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
token-olc:      ## Mac: çıktı biçimlerinin token sayısı (Adım 2, P3)
	python3 tools/token_olc.py --server .spike/llama.cpp/build/bin/llama-server --model .spike/gguf/C-Q4_K_M.gguf
veri:           ## Adım 3: sentetik veri üret (deterministik)
	python tools/veri_uret.py
veri-istatistik:
	python tools/veri_istatistik.py
incele:         ## Adım 3: golden set için 150 örneği elle incele (kaldığın yerden devam eder)
	python tools/incele.py
golden:
	python tools/incele.py --birlestir
dis-veri:       ## OLTA-TR + UCI indir (repoya girmez)
	python data/external/download.py
llm-paket:      ## golden ön-eleme paketi → data/golden/llm_paketi.md (Gemini'ye yükle)
	python tools/llm_inceleme.py disari
llm-iceri:      ## Gemini cevabı data/golden/llm_cevap.json → kararlar
	python tools/llm_inceleme.py iceri
teyit:          ## yalnızca LLM'in işaretledikleri + 20 rastgele "doğru"
	python tools/incele.py --teyit
eval:           ## Adım 4: kural + tfidf, tüm setler (dış setler dahil) → eval/results
	python -m eval.run_eval
eval-hizli:     ## dış setleri atla
	python -m eval.run_eval --set golden dogrulama adversarial
rapor:          ## eval/results → docs/eval-report.md (otomatik bölüm)
	python -m eval.report
