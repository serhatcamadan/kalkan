# KALKAN v6.0 · 2026-11-19
.PHONY: yeniden-puanla eval-gpt-pilot eval-gpt eval-gpt-ekonomik sunucu-08 sunucu-2b eval-zs-08 eval-zs-2b eval eval-hizli rapor llm-paket llm-iceri teyit veri veri-istatistik incele golden dis-veri token-olc spike gguf-2b bench-mac bench test lint clean-spike
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

LLAMA_SERVER = .spike/llama.cpp/build/bin/llama-server
SUNUCU_ARG   = --host 127.0.0.1 --port 8080 -c 4096 -np 1 --jinja
sunucu-08:      ## Adım 5: Qwen3.5-0.8B zero-shot (ayrı terminalde açık kalsın)
	$(LLAMA_SERVER) -m .spike/gguf/C-Q4_K_M.gguf $(SUNUCU_ARG)
sunucu-2b:
	$(LLAMA_SERVER) -m .spike/gguf/C2B-Q4_K_M.gguf $(SUNUCU_ARG)
DIS_LIMIT ?= 300
eval-zs-08:     ## sunucu-08 açıkken: golden + doğrulama + adversarial + dış setler (örneklem)
	python -m eval.run_eval --model llm --etiket zs-0.8b --set golden dogrulama adversarial
	python -m eval.run_eval --model llm --etiket zs-0.8b --set olta uci --limit $(DIS_LIMIT)
eval-zs-2b:     ## sunucu-2b açıkken
	python -m eval.run_eval --model llm --etiket zs-2b --set golden dogrulama adversarial
	python -m eval.run_eval --model llm --etiket zs-2b --set olta uci --limit $(DIS_LIMIT)

# Adım 6 — gpt-5.4-mini (BYOK). Anahtar YALNIZCA terminal ortam değişkeninde: read -s OPENAI_API_KEY; export OPENAI_API_KEY
eval-gpt-pilot: ## 20 golden örnek, en fazla $0.03 → gerçek mesaj başı maliyeti ölç
	python -m eval.run_eval --model llm --etiket gpt-5.4-mini --byok --akil none --set golden --pilot 20 --butce-usd 0.03
eval-gpt:       ## SEÇENEK A (tam): golden 297 + adversarial 30 (≤ $0.42) ve OLTA 50 (≤ $0.10) ≈ $0.47
	python -m eval.run_eval --model llm --etiket gpt-5.4-mini --byok --akil none --set golden adversarial --butce-usd 0.42
	python -m eval.run_eval --model llm --etiket gpt-5.4-mini --byok --akil none --set olta --limit 50 --butce-usd 0.10
eval-gpt-ekonomik: ## SEÇENEK B: golden 150 (tür başına eşit, sabit) + adversarial 30 (≤ $0.24) ve OLTA 50 (≤ $0.10) ≈ $0.30
	python -m eval.run_eval --model llm --etiket gpt-5.4-mini --byok --akil none --set golden adversarial --golden-limit 150 --butce-usd 0.24
	python -m eval.run_eval --model llm --etiket gpt-5.4-mini --byok --akil none --set olta --limit 50 --butce-usd 0.10
yeniden-puanla: ## politika değişince tüm LLM sonuçlarını model çağırmadan yeniden puanla ($0)
	python -m eval.yeniden_puanla
