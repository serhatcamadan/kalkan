# KALKAN v7.0 · 2026-11-19
.PHONY: api api-deneme eval-kor kor-ozet eval-sistem egit-v3 loss-v3 kontrol-v3 sablon-paket-15 sablon-iceri-15 katmanli export-ft sunucu-ft gguf-parite gguf-parite-sema eval-ft sft-veri sablon-parite egit-08 loss kontrol-08 kontrol-08-it sablon-paket sablon-iceri egit-v2 loss-v2 kontrol-v2 kontrol-08-temel yeniden-puanla eval-gpt-pilot eval-gpt eval-gpt-ekonomik sunucu-08 sunucu-2b eval-zs-08 eval-zs-2b eval eval-hizli rapor llm-paket llm-iceri teyit veri veri-istatistik incele golden dis-veri token-olc spike gguf-2b bench-mac bench test lint clean-spike
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

# Adım 8 — fine-tune modeli: GGUF + parite + tam eval
FTV  ?= v3
IT_SEC ?= 450
ADP  ?= training/adapters/ft-0.8b-$(FTV)-it$(IT_SEC)
FTAD ?= kalkan-0.8b-$(FTV)
Q    ?= Q8_0
api:            ## Adım 10: API + demo arayüzü (sunucu-ft açıkken) → http://127.0.0.1:8000
	KALKAN_DENETIM_YOL=logs/denetim.jsonl uvicorn kalkan.api:uygulama --factory --host 127.0.0.1 --port 8000 --no-server-header
api-deneme:     ## api açıkken: üç istek + sağlık (mesaj metni denetim kaydına girmemeli)
	@curl -s http://127.0.0.1:8000/saglik; echo
	@curl -s -X POST http://127.0.0.1:8000/analiz -H 'Content-Type: application/json' \
	  -d '{"mesaj":"Kestane Kargo: gönderiniz gümrükte. 49,90 TL ödeyin: kstn-kargo.info/ode"}' | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['risk'], d['tur'], d['sure_ms'], 'ms')"
	@curl -s -o /dev/null -w "boş mesaj → %{http_code}\n" -X POST http://127.0.0.1:8000/analiz -H 'Content-Type: application/json' -d '{"mesaj":""}'
	@tail -1 logs/denetim.jsonl
eval-kor:       ## Adım 9b: KÖR saldırı seti, BİR KEZ (sunucu-ft açıkken) · kural, tfidf, ft tek başına, sistem
	python -m eval.run_eval --set kor
	python -m eval.run_eval --model llm --etiket ft-0.8b-$(FTV)-$(Q) --istem kisa --set kor
	python -m eval.run_eval --model llm --etiket sistem-$(FTV)-$(Q) --istem kisa --katman --set kor adversarial
	$(MAKE) --no-print-directory kor-ozet
kor-ozet:       ## kör set: hangi saldırı sızdı, hangi meşru alarm aldı (metin yok, yalnızca id + saldırı türü)
	python -c "import json,glob; [print(f.split('/')[-1][:-10].ljust(18), 'sızıntı', [(x['id'], x['saldiri']) for x in d['metrikler']['sizintilar']], '· yanlış alarm', [x['id'] for x in d['metrikler']['yanlis_alarmlar']]) for f in sorted(glob.glob('eval/results/*__kor.json')) for d in [json.load(open(f))]]"
eval-sistem:    ## Adım 9a: ÜRÜN YOLU uçtan uca (servis, katman=True) · sunucu-ft FTV=v3 açıkken → sistem-v3-Q8_0
	python -m eval.run_eval --model llm --etiket sistem-$(FTV)-$(Q) --istem kisa --katman --set golden dogrulama adversarial
	python -m eval.run_eval --model llm --etiket sistem-$(FTV)-$(Q) --istem kisa --katman --set olta uci --limit $(DIS_LIMIT)
katmanli:       ## Adım 8b: kural + ft katmanlı karar, çevrimdışı ($0) → eval/results/katmanli__*.json
	python -m eval.katmanli --ft ft-0.8b-$(FTV)-$(Q)
export-ft:      ## adaptör → .spike/gguf/$(FTAD)-{Q4_K_M,Q8_0}.gguf (B yolu, f32 birleştirme)
	bash training/export_gguf.sh $(ADP) $(FTAD)
sunucu-ft:      ## ayrı terminalde açık kalsın: make sunucu-ft Q=Q8_0 | Q=Q4_K_M
	$(LLAMA_SERVER) -m .spike/gguf/$(FTAD)-$(Q).gguf $(SUNUCU_ARG)
gguf-parite:    ## sunucu-ft açıkken; Q, sunucudaki ile AYNI olmalı
	python training/gguf_parite.py --etiket $(FTV)-$(Q) --mlx ft-0.8b-$(FTV)-it$(IT_SEC)
gguf-parite-sema:
	python training/gguf_parite.py --etiket $(FTV)-$(Q) --mlx ft-0.8b-$(FTV)-it$(IT_SEC) --sema
eval-ft:        ## sunucu-ft açıkken, AYNI FTV/Q ile: make eval-ft FTV=v3 → sonuç adı ft-0.8b-v3-Q8_0
	python -m eval.run_eval --model llm --etiket ft-0.8b-$(FTV)-$(Q) --istem kisa --set golden dogrulama adversarial
	python -m eval.run_eval --model llm --etiket ft-0.8b-$(FTV)-$(Q) --istem kisa --set olta uci --limit $(DIS_LIMIT)
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

# Adım 7 — MLX LoRA fine-tune (Mac). MLX komutları spike'ın venv'ini kullanır.
MLXPY = .spike/venv-mlx/bin/python
sft-veri:       ## eğitim/doğrulama → data/sft (kısa sistem istemi + kompakt JSON hedef)
	python training/build_sft.py
sablon-parite:  ## eğitimden ÖNCE: MLX sohbet formatı = llama-server istemi mi? (mask_prompt doğru yerde mi?)
	$(MLXPY) training/sablon_parite.py
egit-08:        ## LoRA eğitimi (training/lora.yaml) → training/adapters/ft-0.8b-v1, log → training/logs
	bash training/train.sh training/lora.yaml
loss:           ## kayıp eğrisi → training/logs/*.png + docs/img/
	python training/loss_egrisi.py training/logs/ft-0.8b-v1.log
kontrol-08:     ## MLX'te doğrulama seti: JSON / tür / alıntı (adaptörlü)
	$(MLXPY) training/hizli_kontrol.py --adapter training/adapters/ft-0.8b-v1
AD ?= ft-0.8b-v1
kontrol-08-it:  ## kontrol noktası: make kontrol-08-it IT=300 [AD=ft-0.8b-v2]  (→ training/adapters/$(AD)-it300/)
	@test -n "$(IT)" || { echo "IT=<iterasyon> ver, ör. make kontrol-08-it IT=300"; exit 1; }
	@d=training/adapters/$(AD)-it$(IT); k=training/adapters/$(AD)/$$(printf %07d $(IT))_adapters.safetensors; \
	  test -f $$k || { echo "$$k yok"; exit 1; }; mkdir -p $$d; \
	  cp training/adapters/$(AD)/adapter_config.json $$d/ && cp $$k $$d/adapters.safetensors && echo "▶ $$d"
	$(MLXPY) training/hizli_kontrol.py --adapter training/adapters/$(AD)-it$(IT)
sablon-paket:   ## Adım 7b: yeni şablonlar → data/templates/inceleme/paket.md (Gemini'ye yükle)
	python tools/sablon_inceleme.py disari
sablon-iceri:   ## Gemini cevabı data/templates/inceleme/cevap.json → işaretlenen şablonlar
	python tools/sablon_inceleme.py iceri
egit-v2:        ## Adım 7b: LoRA v2 (şablon v1.3, ~1 epoch) → training/adapters/ft-0.8b-v2
	bash training/train.sh training/lora_v2.yaml
loss-v2:
	python training/loss_egrisi.py training/logs/ft-0.8b-v2.log
egit-v3:        ## Adım 8c: LoRA v3 (sınıf dengesi %40 meşru) → training/adapters/ft-0.8b-v3
	bash training/train.sh training/lora_v3.yaml
loss-v3:
	python training/loss_egrisi.py training/logs/ft-0.8b-v3.log
kontrol-v3:     ## v3'ün 4 kontrol noktası (~25 dk)
	for it in 300 450 600 750; do $(MAKE) --no-print-directory kontrol-08-it AD=ft-0.8b-v3 IT=$$it || exit 1; done
sablon-paket-15: ## Adım 8c: yalnızca yeni 16 meşru/reklam şablonu → data/templates/inceleme/paket_15.md
	python tools/sablon_inceleme.py disari --ilk 15
sablon-iceri-15:
	python tools/sablon_inceleme.py iceri --ilk 15
kontrol-v2:     ## v2'nin 4 kontrol noktasını sırayla ölç (~25 dk) → training/logs/kontrol__*.json
	for it in 300 450 600 750; do $(MAKE) --no-print-directory kontrol-08-it AD=ft-0.8b-v2 IT=$$it || exit 1; done
kontrol-08-temel: ## aynı ölçüm adaptörsüz (öncesi)
	$(MLXPY) training/hizli_kontrol.py --temel
