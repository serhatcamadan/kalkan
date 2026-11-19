# ADR-0001: Fine-tune → Ollama dönüşüm yolu

- **Durum:** Kabul edildi · 2026-11-19 (spike 01)
- **Tarih:** 2026-11-18

## Bağlam
Model MLX'te (Mac) LoRA ile eğitilecek, canlıda Ollama + GGUF Q4_K_M ile çalışacak (Mac ve 6 GB'lık VPS).
Qwen3.5 hibrit bir mimari (Gated DeltaNet + tam dikkat) ve checkpoint görsel kuleli. Dönüşüm araçları
bu mimari için yeni, MLX'in iç ağırlık düzeni de HF'den farklı olabilir.

## Seçenekler
1. **A:** `mlx_lm fuse` → `convert_hf_to_gguf` → `llama-quantize`
2. **B:** MLX adaptörünü orijinal HF ağırlıklarına kendi script'imizle birleştir → `convert_hf_to_gguf` → `llama-quantize`
3. **Colab QLoRA (PEFT)** → `merge_and_unload` → GGUF (yedek yol, Adım 7)
4. `ollama create -q q4_K_M`: güncel Ollama'da GGUF için desteklenmiyor, **elendi** (spike D0 ile teyit edilecek)

## Karar
**B yolu.** MLX'te eğitilen LoRA adaptörü, `training/spike/merge_mlx_adapter_hf.py` ile orijinal HF
checkpoint'ine birleştirilir. Ardından `convert_hf_to_gguf.py` → `llama-quantize Q4_K_M` (sabit llama.cpp commit'i).

Kanıt (spike 01):
- A (`mlx_lm fuse`): 61 norm tensöründe +1 ofset, farklı tensör isimleri ve conv yerleşimi. Tokenizer sınıf adı
  dönüştürücünün tanımadığı biçimde yazılmış → dönüşüm hata verdi. Hata çıkmasaydı sessiz bozulma riski vardı.
- B: inspect'te sorun yok, GGUF llama-cli'de doğru cevap verdi.
- `ollama create -q q4_K_M`: GGUF için desteklenmiyor (D0 hatası birebir).

## Sonuçlar
- Kuantizasyon her zaman `llama-quantize` ile. llama.cpp commit'i `versions.lock` dosyasında sabit.
- Adım 7'de MLX sürümü değişirse önce `inspect_weights.py` yeniden koşulur.
- Yedek yol (Colab QLoRA → PEFT merge) aynı `convert_hf_to_gguf` hattına girer.
