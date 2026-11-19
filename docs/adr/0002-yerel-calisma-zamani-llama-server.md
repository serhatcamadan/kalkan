# ADR-0002: Yerel çalışma zamanı — Ollama yerine llama-server

- **Durum:** Kabul edildi
- **Tarih:** 2026-11-19

## Bağlam
Spike 01'de kendi dönüştürdüğümüz Qwen3.5 GGUF'u (hem fine-tuned B hem eğitilmemiş C) Ollama 0.40.14'te
`tensor 'blk.0.ssm_beta.weight' not found` hatasıyla açılmadı. Aynı dosya, onu üreten llama.cpp commit'iyle
(`5812201a8`) doğru cevap verdi (83.6 tok/s, M4). Ollama'nın kendi kütüphane modeli çalışıyor.
Sorun: Ollama'nın içindeki llama.cpp, dönüştürücümüzden geride. Qwen3.5 gibi yeni mimarilerde bu fark sık açılıyor.

## Seçenekler
1. **llama-server (llama.cpp)**: GGUF'u üreten commit'le aynı commit'te çalıştır.
2. Ollama'nın gömülü llama.cpp sürümünü bulup ona uygun eski dönüştürücü kullanmak: her Ollama güncellemesinde kırılabilir.
3. Ollama'nın kendi kütüphane modelini kullanmak: fine-tuned modeli içine koyamıyoruz.

## Karar
**Seçenek 1.** Yerel model llama-server ile, OpenAI uyumlu `/v1/chat/completions` üzerinden sunulur.
llama.cpp commit'i dönüştürme ile çalıştırma arasında **sabit ve aynı** tutulur (Mac, Docker, VPS).

## Gerekçe
- **Tek doğruluk kaynağı:** Test ettiğimiz dosya + commit, canlıda çalışanla aynı. Arada ikinci bir motor yok.
- **Tek arka uç:** Yerel mod ve BYOK aynı OpenAI uyumlu istemciyle konuşur (`backends/openai_compat.py`).
- llama-server JSON şemasıyla kısıtlı üretim, prompt önbelleği (`cache_prompt`), `/health` ve
  istek başına `timings` sunar. Bunlar eval ve benchmark için doğrudan kullanılır.
- Adil karşılaştırma: zero-shot (C) ve fine-tuned (B) aynı hattan geçer. H4 (kuantizasyon kaybı) temiz ölçülür.

## Bedeli
- Ollama'nın model yönetimi (pull, keep_alive, çoklu model) yok. Tek modelli bir servis için gerekmiyor.
- llama.cpp'yi Docker imajında sabit commit'le derlemek gerekecek (Adım 10).
- README'deki "Ollama ile yerel mod" vaadi → "tek komutla llama-server ile yerel mod" olarak güncellendi.
