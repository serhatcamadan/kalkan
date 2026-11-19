# ADR-0001: Fine-tune → Ollama dönüşüm yolu

- **Durum:** Önerildi (spike 01 sonucuyla kesinleşecek)
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
_Spike sonrası:_ C ↔ A ↔ B smoke ve inspect sonuçlarına göre.
Ön tercih: **B**. Gerekçe: llama.cpp'nin test edildiği orijinal HF düzenine dokunmuyor, yalnızca LoRA
hedeflerini değiştiriyor. Fark ölçülebilir (`inspect_weights.py`), görsel kule korunuyor (v2 için).

## Sonuçlar
- Kuantizasyon her zaman `llama-quantize` ile yapılır. Sürümler `versions.lock` dosyasına yazılır.
- Adım 8'deki parite testi (MLX ↔ GGUF) bu yolun üzerine kurulur.
