# Adım 9 — katmanlı kararın servise taşınması ve güvenlik · v1 · 2026-11-22

## 9a — katmanlı karar ürün yolunda ("ölçülen = çalışan")

**Sorun:** ADR-0006 kararı `eval/katmanli.py` içinde, çevrimdışı ölçülmüştü; `kalkan/service.py` hâlâ yalnızca model
yolunu çalıştırıyordu. Değerlendirmede ölçülen sistem ile kullanıcıya çalışan sistem farklıydı.

**Değişiklikler:**
| Dosya | Ne |
|---|---|
| `kalkan/kural.py` (yeni) | Kural mantığı `eval/modeller/kural.py`'den pakete taşındı: `kural_ciktisi(girdi, tipler)`. Davranış birebir aynı (golden 297/297, adversarial 30/30 aynı çıktı; testli). |
| `kalkan/katman.py` (yeni) | `katmanla()`: ★ ikinci_talep kuralları tek yerde. Ürün ve değerlendirme bunu çağırır. |
| `kalkan/service.py` v1.1 | `analiz(..., katman=True)` = ürün yolu. `hazirla()` ve `kural_karari()` dışa açık; `eval/katmanli.py` aynılarını kullanır. `Iz`'e `kural_tur`, `kural_risk`, `model_risk`, `katman_kaynak` eklendi. |
| `kalkan/__main__.py` v1.1 | CLI artık ürün yolunu çalıştırır (`--yalniz-model` ile eski davranış). |
| `eval/katmanli.py` v1.1 | ★ satırı `katmanla()` ile hesaplanır. |
| `eval/run_eval.py`, `eval/modeller/llm.py` | `--katman`: servisi uçtan uca ölçer → `make eval-sistem`. |
| `tests/test_katman.py` (yeni) | Katman kuralları + **tekrar oynatma**: kaydedilmiş model çıktıları sahte bir arka uçla servise verilir; servisin riski `eval/katmanli.py` ★ ile örnek örnek aynı olmalı. |

**Yeni kural (fail-closed, ADR-0005 ile tutarlı):** kural "düşük" dedi ama model cevap veremedi (bağlantı, zaman
aşımı, bozuk şema) → **belirsiz**. Ürün "düşük" demek için iki katmanın da onayını ister. Kural orta/yüksek dediyse
model düşse de o karar kalır. Kayıtlı sonuçlarda model hatası 0 olduğu için ölçülen sayılar değişmez.

**Küçük fark:** kural katmanı artık ürün gibi kırpılmış girdinin (2.000 karakter) sinyallerini kullanıyor; eski
değerlendirme tam metni kullanıyordu. Yalnızca 2.000 karakteri aşan e-postalarda (OLTA/UCI) fark eder.

### Tahminler (`make eval-sistem`, gerçek llama-server ile)
| # | Tahmin |
|---|---|
| S1 | golden: recall 1.000, FPR 0.018, makro-F1 0.905: çevrimdışı ★ ile **birebir** (tekrar oynatma testi bunu zaten garanti ediyor; gerçek koşu deterministik üretimi de doğrular) |
| S2 | adversarial sızıntı 0 |
| S3 | OLTA/UCI ayırt etme çevrimdışı ★'dan en çok ±0.02 farklı (kırpma farkı) |
| S4 | p95 (Mac) yalnızca model yolundan ≤ 10 ms fazla (kural katmanı ~2 ms) |

### Sonuçlar
`make test`: 90 passed (tekrar oynatma testleri gerçek ft-v3 çıktılarıyla golden/doğrulama/adversarial'da geçti).

| set (`make eval-sistem`, gerçek llama-server) | makro-F1 | recall | FPR | sızıntı | p95 ms (Mac) | çevrimdışı ★ |
|---|---|---|---|---|---|---|
| golden | **0.9055** | **1.000** | **0.0185** | – | 1.264 | 0.905 / 1.000 / 0.018 ✅ birebir |
| doğrulama | 0.758 | 0.963 | 0.056 | – | 1.279 | 0.758 / 0.963 / 0.056 ✅ |
| adversarial | – | – | – | **0** | 1.331 | 0 ✅ |
| OLTA | – | 0.665 | 0.542 | – | 1.737 | 0.665 / 0.542 ✅ |
| UCI | – | 0.558 | 0.511 | – | 2.394 | 0.558 / 0.511 ✅ |

**Karne:** S1 ✅ birebir · S2 ✅ · S3 ✅ (UCI ★ ayırt +0.036 → +0.047, OLTA değişmedi) · S4 ✅ (p95 yalnızca model
yolunun 1.614 ms'sinden bile düşük: ölçüm gürültüsü; kural katmanı ~2 ms).

**Yan bulgu:** kırpma değişikliği **kural** katmanını UCI'de belirgin değiştirdi (ayırt +0.120 → +0.050): uzun
e-postalarda kuralın yakaladığı işaretlerin bir kısmı 2.000 karakterden sonra. Ürün zaten ilk 2.000 karakteri
görüyor; yani önceki +0.120 ürünün değil, tam metni gören bir kuralın sayısıydı. 9b'deki kırpma saldırısı testi
aynı zayıflığın saldırgan tarafı.

**CLI örneği katmanın değerini gösteriyor:** "Paketiniz gümrükte, 49,90 TL ödeyin: bit.ly/x9k2" → model türü
`sahte_kamu_gorevlisi` (yanlış), kural `sahte_kargo_gumruk` (doğru) → kullanıcı kuralın türünü ve modelin
kapıdan geçen alıntılarını görür; risk yüksek, kaynak "kural". 708 ms.

## 9b — güvenlik (sonraki mesaj)
Kör adversarial örnekler, 2.000 karakter kırpma saldırısı, BYOK anahtarı log testi, denetim kaydı (metinsiz),
hız sınırı (API ile Adım 10'da).
