# 🛡️ Kalkan — Türkçe Dolandırıcılık Mesajı Analizcisi

> Şüpheli bir Türkçe mesajı (SMS, WhatsApp, e-posta) alır; **risk**, **tür**, mesajdan **birebir kanıt
> alıntıları** ve **önerilen aksiyon** döndürür. Kanıtları model uyduramaz, çünkü kod doğrular.
> Sistem hiçbir zaman "güvenli" demez.

**Ana soru:** Spam/ham ayrımı çözülmüş bir problem. Bu projede ölçtüğüm şey şu: bir bankada *hangi model
yeter* ve cevabına *neden güvenilebilir*? Karşılaştırılan modeller: kural tabanlı · TF-IDF · zero-shot
küçük model · fine-tuned küçük model · gpt-5.4-mini.

> ⚠️ Yapım aşamasında. Portfolyo serisi 1/3 (A Kalkan → D KAP Kanıt Analisti → G B2B Sipariş Ajanı).

## Durum
| # | Adım | Durum |
|---|---|---|
| 1 | Repo iskeleti ✅ · dönüşüm spike'ı ✅ (B yolu + llama-server) · VPS benchmark 🔄 | 🔄 |
| 2 | Taksonomi, şema, sinyaller, PII | ⏳ |
| 3–12 | Veri, eval, pipeline, fine-tune, güvenlik, demo, VPS, yazım | ⏳ |

## Hızlı başlangıç (şimdilik)
```bash
make spike          # Mac (Apple Silicon): MLX LoRA → GGUF → Ollama boru hattı testi
make bench-mac      # Mac: llama-server gecikme ölçümü
# VPS: deploy/ içinde → bash bench_vps.sh
make test
```

## Belgeler
- [Spike 01 — dönüşüm yolu](docs/spike-01-donusum.md)
- [ADR-0001 dönüşüm yolu](docs/adr/0001-finetune-donusum-yolu.md) · [ADR-0002 llama-server](docs/adr/0002-yerel-calisma-zamani-llama-server.md)

## Lisans ve veri
Gerçek kişisel veri kullanılmaz. Kurum adları kurgusaldır. Linkler hiçbir zaman ziyaret edilmez, yalnızca statik analiz yapılır.
