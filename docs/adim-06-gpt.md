# Adım 6 — gpt-5.4-mini taban çizgisi (BYOK) · v1 · 2026-11-20

## Soru
Adım 5'te zero-shot Qwen3.5 0.8B/2B başarısız oldu. Sebep **istem/görev tanımı** mı, **model ölçeği** mi?
Aynı istem, aynı hat (sinyal → maske → model → kapı → politika), farklı model: gpt-5.4-mini.
- gpt-5.4-mini de kötüyse → istemi/görevi düzelt, sonra fine-tune.
- İyiyse → sorun ölçek; gpt-5.4-mini fine-tune'un hedeflediği üst çizgi olur (H1).

## Kurulum kararları (2026-11-20 doğrulandı)
- Fiyat ($/1M token): girdi 0.75 · önbellekli girdi 0.075 · çıktı 4.50. Sistem istemi her istekte aynı → önbellek.
- Akıl yürütme modeli: akıl yürütme token'ları çıktı fiyatından faturalanır. Bütçe için `reasoning_effort=none`
  (yol haritasında "düşük" yazıyordu; pilot maliyetine göre gerekirse küçük bir "low" karşılaştırması).
- `max_completion_tokens` kullanılır, sıcaklık/tohum gönderilmez (akıl yürütme modelleri reddeder).
- Strict şema bazı anahtar kelimeleri (maxItems/maxLength) desteklemeyebilir → hat, 3'ten fazla kanıtı ve 80 karakteri
  aşan alıntıyı ATAR (tüm cevabı çöpe atmaz). Aynı kural yerel modeller için de geçerli (adil karşılaştırma).
- **UCI dış API'ye gönderilmez** (gerçek kişisel e-postalar). Kodda engelli. OLTA sentetik → gönderilebilir.
- Bütçe koruması: `--butce-usd` aşılınca çalıştırma durur, kısmi sonuç yazılır.
- Anahtar yalnızca ortam değişkeninde. Repr'de görünmez, sonuç dosyasına yazılmaz (sahte sunucuyla doğrulandı).

## Tahminler (çalıştırmadan önce)
| # | Tahmin |
|---|---|
| G1 | golden tür makro-F1 0.70–0.85 (zero-shot 2B'nin 0.24'ünün çok üstünde, kural modelinin 0.89'una yakın veya altında) |
| G2 | golden meşru FPR ≤ 0.10 |
| G3 | kapı öncesi kanıt geçerliliği ≥ 0.90, kanıt eşleşme F1 0.40–0.60 |
| G4 | **OLTA ayırt etme (recall − FPR) ≥ 0.50** (TF-IDF 0.21, 2B 0.09): dünya bilgisi e-postaya taşınır |
| G5 | adversarial sızıntı 0 |
| G6 | golden 297 maliyeti $0.10–0.20, p95 1.5–3 sn |

## Sonuçlar
(`make eval-gpt-pilot` → `make eval-gpt` → `make rapor`)
