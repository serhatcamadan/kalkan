# Kalkan v1.0.0 · 2026-11-23

İlk tam sürüm: değerlendirilen sistem ile yayındaki sistem bu etikette aynı.

**Canlı demo:** https://kalkan-serhat.duckdns.org

## Ne var
- Türkçe SMS/WhatsApp dolandırıcılık analizi: risk, olası tür, mesajdan birebir kanıt alıntıları, öneri
- Katmanlı karar: kural sistemi birinci katman, ince ayarlı Qwen3.5-0.8B (LoRA v3, GGUF Q8_0) ikinci görüş
- Tamamen yerel çalışma (llama.cpp, commit 5812201a8); mesaj sunucudan çıkmaz
- FastAPI + tek sayfalık arayüz, Docker Compose (llama + api + Caddy / Let's Encrypt)

## Sonuçlar (golden, 297 sentetik mesaj, tam sistem)
| | makro-F1 | recall | meşru FPR | sızıntı |
|---|---|---|---|---|
| Kalkan (kural + 0.8B, katmanlı) | 0.905 | 1.000 | 0.019 | 0 / 30 |
| gpt-5.4-mini (karşılaştırma) | 0.905 | 1.000 | 0.000 | 0 / 30 |

Kör saldırı seti: 19 saldırıdan 1'i sızıyor. Canlı p95 (HTTPS, 4 vCPU VPS): 6,9 sn.

## Sınırlar
Sentetik veri; FPR için %95 aralık [0.003, 0.098]; e-posta için uygun değil; bilinen kaçırma ve yanlış alarmlar
README'nin "Sınırlar" bölümünde.

Ayrıntı: README · docs/rapor.md · docs/adr/0006-model-secimi-katmanli-karar.md
