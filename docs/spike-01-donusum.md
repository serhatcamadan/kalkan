# Spike 01 — Dönüşüm yolu (Adım 1) · v1 · 2026-11-18

**Soru:** MLX'te LoRA ile eğitilmiş Qwen3.5-0.8B, Ollama'da Q4_K_M olarak doğru cevap veriyor mu?
**Yöntem:** 1 iterasyonluk LoRA (kalite değil, boru hattı testi), üç yol + bir kontrol.

| Yol | Akış |
|---|---|
| C (kontrol) | HF bf16 → `convert_hf_to_gguf` → `llama-quantize Q4_K_M` → Ollama |
| A | MLX LoRA → `mlx_lm fuse` → GGUF → Q4_K_M → Ollama |
| B | MLX LoRA → kendi birleştirme script'imiz (orijinal HF düzeni korunur) → GGUF → Q4_K_M → Ollama |
| D0 | Yol haritasındaki `ollama create -q q4_K_M` (BF16 GGUF'tan) |

## Web'den doğrulanan bilgiler (18.11.2026)
- `Qwen/Qwen3.5-0.8B`: Apache-2.0, `image-text-to-text`, model_type `qwen3_5`, yani **görsel kuleli** bir checkpoint. Varsayılan modu düşünmesiz (non-thinking).
- mlx-lm'in `qwen3_5` yükleyicisi görsel tensörleri yüklemeden önce atıyor (`sanitize()`).
- Ollama 0.34.1 ve sonrasında `ollama create --quantize q4_K_M` **çalışmıyor**: safetensors için yalnızca MLX biçimleri (int4/int8/nvfp4/mxfp4/mxfp8) kabul ediliyor, GGUF'ta ise oluşturma anında kuantizasyon hiç yok. `ADAPTER` talimatı kaldırılmış. Güncel sürüm 0.40.x.
- llama.cpp'de Qwen3.5 dönüşüm desteği sık değişiyor; "BPE pre-tokenizer tanınmadı" hatasının en olası nedeni tokenizer dosyalarının kaybolması veya eski bir commit.
- mlx-lm'in son sürümü kaynağa göre farklı görünüyor: GitHub sayfasında v0.31.3, bir izleyicide v0.32.2 (16.10.2026). Script `MLX_LM_VERSION` değişkeniyle sabitliyor; varsayılan 0.32.2. `pip index versions mlx-lm` ile kontrol et.

## Tahminler (spike ÖNCESİ yazıldı)
| # | Tahmin | Güven |
|---|---|---|
| T1 | C (kontrol) dönüşür ve Ollama'da anlamlı Türkçe cevap verir | %85 |
| T2 | **A kırılır veya bozuk çıktı verir**: MLX tensör isimleri/conv yerleşimi/norm +1 ofseti HF'den farklı | %55 |
| T3 | B çalışır ve çıktısı C'ye neredeyse eşittir (benzerlik ≥ 0.9) | %80 |
| T4 | D0 `unsupported --quantize` hatası verir → `llama-quantize` zorunlu | %90 |
| T5 | Boyutlar: BF16 GGUF ≈ 1.5–1.8 GB, Q4_K_M ≈ 0.5–0.6 GB | %75 |
| T6 | 1 iterasyon LoRA < 1 dk. Spike'ın tamamı 20–40 dk sürer, çoğu indirme ve derleme | %70 |
| T7 | Mac'te 0.8B Q4 üretim hızı 80–150 tok/s | %60 |
| T8 | Think sızıntısı yok (0.8B varsayılan olarak düşünmesiz) | %80 |

**VPS tahmini (bench_vps.py ile ölçülecek):** E5-2699 v4, 4 vCPU, yalnızca AVX2.
- 0.8B Q4: üretim 12–25 tok/s, prompt 40–90 tok/s. Prompt ~450 token + çıktı 96 token için p95 ≈ 9–16 sn, **sınırda**.
- 2B Q4: üretim 5–10 tok/s, prompt 15–35 tok/s. **p95 > 15 sn olacak (%75)**.
- Sonuç: 15 sn eşiğini tutturmak için çıktı kısa olmalı (kanıt-önce kompakt JSON, en fazla 3 kanıt). Sistem istemi de kısaltılmalı ya da KV önbelleği yeniden kullanılmalı. Fine-tune'un gizli bir kazancı da bu olabilir: kısa sistem istemi yetiyor.

## Sonuçlar (spike SONRASI doldur)
| Adım | Durum | Süre | Not |
|---|---|---|---|
| 3b LoRA 1 iter | | | |
| 4a fuse (A) | | | |
| 4b merge (B) | | | |
| 4c/4d inspect | | | norm +1? yerleşim farkı? |
| 5c/5a/5b GGUF | | | |
| 6* Ollama | | | |
| 6d D0 `-q` | | | |
| 7 smoke | | | benzerlik A/B ↔ C |

Tahmin tuttu mu? T1 … T8 → ✅ / ❌ ve neden.
**Karar → ADR-0001.**
