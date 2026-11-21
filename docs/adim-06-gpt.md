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

## Pilot (20 golden, 2026-11-21)
makro-F1 0.926 · doğruluk 0.95 · meşru FPR 0.00 · kanıt geçerliliği 0.95 · eşleşme F1 0.73 · p95 1.6 sn · **$0.0231**.
İlk deneme (2026-11-20) tüm isteklerde hata verdi, maliyet $0. Kod hatayı kaydetmiyordu → v1.1: hata kaydı,
3 ardışık cevapsızlıkta durma, 400'de şema/akıl parametresi uyarlaması.

**Maliyet sürprizi:** mesaj başı ~$0.0012 (tahmin ~$0.0005). Olası sebep: sistem istemi OpenAI önbelleğinin
asgari uzunluğunun (1.024 token) altında, indirim devreye girmiyor. Ayrıca Türkçe, OpenAI tokenizer'ında beklenenden
çok token'a bölünüyor. Ders: pilot olmadan tam koşu bütçeyi aşacaktı (eski sınırlar golden'ı ~%70'te keserdi).

Ön yorum: aynı istem büyük modelde neredeyse kusursuz → zero-shot küçük modelin sorunu istem değil, ÖLÇEK.

## Sonuçlar (Seçenek A: tam golden, 2026-11-21, reasoning_effort=none)
| | gpt-5.4-mini | kural | 2B zero-shot | TF-IDF |
|---|---|---|---|---|
| golden tür makro-F1 | **0.905** | 0.887 | 0.236 | 0.491 |
| dol. recall / meşru FPR | 0.996 / **0.000** | 0.975 / 0.000 | 0.98 / 0.43 | 1.00 / 0.00 |
| kapı öncesi kanıt geçerliliği | 0.964 | 1.000 | 0.767 | — |
| kanıt eşleşme F1 | **0.770** | 0.713 | 0.021 | — |
| adversarial sızıntı | 1 (adv_21) | 1 | 2 | 2 |
| OLTA recall / FPR → ayırt etme (n=50) | 0.50 / 0.25 → **0.25** | 0.00 | 0.09 | 0.21 |
| p95 · maliyet | 1.39 sn · $0.0012/mesaj | ~0 · $0 | 1.02 sn · $0 | ~0 · $0 |

Harcama: pilot $0.023 + golden $0.356 + adversarial $0.034 + OLTA $0.061 = **$0.474** (A projesi bütçesi $0.60).

## Tahmin karnesi
| # | Tahmin | Sonuç |
|---|---|---|
| G1 | makro-F1 0.70–0.85 | ❌ daha iyi: 0.905 |
| G2 | meşru FPR ≤ 0.10 | ✅ 0.000 |
| G3 | kanıt geçerliliği ≥ 0.90; eşleşme F1 0.40–0.60 | ✅ 0.964 · ❌ eşleşme daha iyi: 0.77 |
| G4 | OLTA ayırt etme ≥ 0.50 | ❌ 0.25 |
| G5 | adversarial sızıntı 0 | ❌ 1 |
| G6 | golden $0.10–0.20, p95 1.5–3 sn | ❌ $0.356 · ✅ 1.39 sn |

## Bulgular
1. **Adım 5'in sorusu cevaplandı: sorun ölçek, istem değil.** Aynı istem ve hatla büyük model 0.905 alıyor.
2. **Sentetik golden doydu.** Kural 0.887, gpt-5.4-mini 0.905. Üst sıradaki modelleri artık dış set, adversarial,
   kanıt kalitesi, maliyet, gecikme ve gizlilik ayırıyor.
3. **OLTA'da sorun model değil, metin-yalnız yaklaşım.** Kaçan 15 oltalamanın incelenen 4'ü de modelce `reklam_spam`:
   seminer daveti, kampanya duyurusu, "güvenlik güncellemesi için bağlantıya göz atın". Metin meşru bir bülten gibi.
   Bu örneklerde oltalamayı belirleyen şey **bağlantının kendisi** (OLTA'nın bir kısmı gerçek zararlı URL içeriyor).
   Kalkan bağlantıları bilerek ziyaret etmiyor ve itibar listesi kullanmıyor (v2: "kötü niyetli URL listesi"). Bu tip
   oltalama metin-yalnız bir sistemin tavanını gösteriyor → README'de **sınırlama** olarak yazılacak.
4. **adv_21 sızıntısı bir politika boşluğuydu.** Emoji dolu "TEBRİKLER… 100 GB HEDİYE… rb.gy/… Son gün" → model
   `reklam_spam` dedi. Kısa link yalnızca "orta" sinyal ve yalnızca `mesru_islem` ile birlikte güvenlik ağını
   tetikliyordu. → **Politika v1.1** (ADR-0005 eki): model "reklam" dese de *resmi olmayan link + yasal ret satırı yok*
   → orta. Gerekçe taksonomide zaten yazılı ("reklam ret mekanizması içerir"; TR'de ticari iletide İYS/ret zorunlu).
   Golden'daki 54 meşru/reklam mesajında doğru türle 0 yanlış alarm (kontrol edildi).
   **Dürüstlük notu:** kural bir test örneğine bakılarak eklendi; adv_21 artık kör değil. Adım 9'da kör yeni
   adversarial örnekler eklenecek.
5. **Politika değişikliği $0.** Model risk üretmediği için `python -m eval.yeniden_puanla`, saklanan ham tür + kanıtlarla
   tüm LLM sonuçlarını (gpt dahil) API çağrısı olmadan yeniden puanlıyor. ADR-0005'in somut faydası.
6. **Karar kuralı:** gpt-5.4-mini sert kısıtı (banka modunda veri TR'de) zaten geçemiyor; rolü **üst çizgi**:
   fine-tune'un (Adım 7–8) ne kadar yaklaştığı buna göre ölçülecek (H1).
