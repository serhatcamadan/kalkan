# Spike 01 — Dönüşüm yolu (Adım 1) · v2 · 2026-11-19 (sonuçlar işlendi)

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

## Sonuçlar (19.11.2026 · Apple M4 16 GB · macOS 15.7.4)
Sürümler: mlx-lm 0.32.2 · mlx 0.32.4 · llama.cpp `5812201a8` (b12544) · transformers 4.57.6 (dönüştürücü) ·
Ollama 0.40.14 · model `Qwen/Qwen3.5-0.8B@2fc0636`

| Adım | Durum | Süre | Not |
|---|---|---|---|
| Kurulum (MLX + llama.cpp derleme) | OK | 35 + 505 sn | Sürenin çoğu derleme |
| Model indirme | OK | 191 sn | |
| LoRA 1 iterasyon | OK | 15 sn | |
| 4a fuse (A) | OK | 3 sn | ama ↓ |
| 4c inspect A | ❌ sorunlu | | isim seti farklı, conv yerleşimi farklı, **61 norm tensöründe +1 kayma** |
| 5a GGUF (A) | FAIL | 2 sn | `Tokenizer class Qwen3_5Tokenizer does not exist`: fuse, tokenizer ayarını dönüştürücünün tanımadığı bir sınıf adıyla yazdı |
| 4b merge (B) + 4d inspect | OK, `sorunlar: []` | 3 + 3 sn | |
| 5c/5b GGUF (C, B) | OK | 29 / 17 sn | BF16 1.5 GB → Q4_K_M 522 MB |
| 6 Ollama create (C, B) | OK | | ama ↓ |
| 7 smoke (Ollama) | **HATA** (script v1 yanlışlıkla OK yazdı) | | `check_tensor_dims: tensor 'blk.0.ssm_beta.weight' not found` |
| 6d D0 `ollama create -q` | FAIL (beklenen) | | `create-time quantization is only supported for safetensors imports` |
| B · llama-cli (aynı commit) | ✅ | | "Türkiye'nin başkenti Ankara'dır." · prompt 105 t/s · üretim **83.6 t/s** |
| Ollama resmi `qwen3.5:0.8b` | ✅ | | "Ankara" |

## Mac ölçümü · llama-server (M4, 10 thread, 5 koşu, JSON şeması zorunlu)
| model | senaryo | p95 sn | üretim tok/s | prompt tok/s | JSON % | alıntı birebir % | RSS GB |
|---|---|---|---|---|---|---|---|
| B (0.8B, 1 iter LoRA) | kisa (96) | 0.97 | 105.9 | 1005 | **0** | – | 0.84 |
| B | kisa_cachesiz | 1.13 | 105.9 | 1622 | **0** | – | 0.88 |
| B | uzun (256) | 2.14 | 102.2 | 977 | 80 | 67 | 0.94 |
| C (0.8B zero-shot) | kisa | 1.10 | 94.5 | 828 | 20 | – | 0.85 |
| C | uzun | 1.93 | 95.1 | 836 | 100 | 64 | 0.89 |
| C2B (2B zero-shot) | kisa | 1.91 | 54.4 | 631 | 40 | 100 | 1.56 |
| C2B | uzun | 2.61 | 54.6 | 618 | 100 | 88 | 1.57 |

Bulgular:
1. **96 token yetmiyor.** Model JSON'u girintili (satır sonu + boşluk) yazıyor. Uzun alıntılarla birlikte
   bütçe dolup cevap yarıda kesiliyor → geçersiz JSON. Benchmark v2 bunu "geçti" sayıyordu, v2.1'de düzeltildi.
   Çözüm adayları (Adım 2/5/7): girintisiz JSON gramer kısıtı, kısa alıntı kuralı, fine-tune ile kompakt çıktı.
2. **Alıntılar %64–88 birebir.** Zero-shot modeller alıntıyı genişletiyor veya değiştiriyor. KAPI (alıntı birebir
   değilse düşür) gereksiz değil, şart. 2B, 0.8B'den belirgin daha sadık (88 vs 64).
3. **Sinyal etiketleri zayıf** ("hesabınız askıya alınmıştır" → `odeme_talebi`). Zero-shot için beklenen. Fine-tune hedefi.
4. Prompt önbelleği Mac'te önemsiz (+0.15 sn), çünkü Metal 1600 tok/s işliyor. VPS'te CPU ile belirleyici olacak.
5. RAM: 0.8B ≈ 0.9 GB, 2B ≈ 1.6 GB → ikisi de 6 GB VPS'e sığar.

## Teşhis
GGUF'umuz **sağlam**: aynı llama.cpp commit'iyle doğru ve hızlı cevap veriyor. Ollama 0.40.14'ün içindeki
llama.cpp motoru daha eski. Yeni dönüştürücünün Qwen3.5 Gated-DeltaNet tensör düzenini (`ssm_beta` beklentisi)
tanımıyor. Ollama'nın kendi kütüphane modeli çalışıyor, çünkü o model Ollama'nın beklediği düzende paketlenmiş.
Sonuç: sorun **dönüştürücü ile çalışma zamanı arasındaki sürüm uyumsuzluğu**.

## Tahminler tuttu mu?
| # | Sonuç |
|---|---|
| T1 C çalışır | ⚠️ Kısmen: GGUF çalışıyor (llama-cli), Ollama'da açılmıyor. Bu riski öngörmedim. |
| T2 A kırılır | ✅ İki ayrı sebeple: tokenizer kayması + ağırlık düzeni (norm +1) |
| T3 B ≈ C | ✅ İnspect temiz, llama-cli doğru. Benzerlik ölçümü llama-server bench'inde. |
| T4 D0 hata verir | ✅ Birebir |
| T5 boyutlar | ✅ 1.5 GB / 522 MB |
| T6 süre 20–40 dk | ❌ ~14 dk (tahmin fazlaydı) |
| T7 Mac 80–150 tok/s | ✅ 83.6 tok/s (llama-cli, Metal) |
| T8 think sızıntısı yok | ✅ llama-cli'de görülmedi |

**Öğrenilen:** Kontrol grubu (C) olmasaydı Ollama hatasını bizim birleştirme script'imize bağlardık.
Kontrol, hatanın yerini tek denemede gösterdi.

## Kararlar
- ADR-0001 → **Kabul: B yolu** (adaptörü orijinal HF ağırlıklarına kendi script'imizle birleştir).
- ADR-0002 → **Kabul: yerel çalışma zamanı = llama-server** (Ollama değil).

## Yol haritasına etkisi
- Adım 5/8/10/11: "Ollama" yerine llama-server. `backends/ollama.py` yerine tek arka uç `openai_compat.py`
  (yerel llama-server ve BYOK aynı kapıdan).
- Zero-shot ve fine-tuned modeller **aynı dönüşüm hattından** geçer (`training/make_gguf.sh`): adil karşılaştırma.
- Adım 8 parite testi: MLX ↔ llama-server (aynı commit).
