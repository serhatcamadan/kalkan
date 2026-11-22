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

## 9b — güvenlik

### 1. Kırpma saldırısı (service v1.2, katman v1.1)
**Açık:** `hazirla()` ham metni 2.000 karakterde kesiyordu; sinyaller, maske, enjeksiyon taraması ve (9a'dan beri)
kural katmanı da kesilmiş metni görüyordu. 2.000 karakter zararsız metin + sonda dolandırıcılık → hiçbir katman
görmez → "düşük". 9a'daki UCI bulgusu (kural ayırt +0.120 → +0.050) aynı açığın ölçümdeki izi.
**Düzeltme:**
- Ham metin `HAM_MAKS` = 10.000 karaktere kadar okunur. Sinyaller, maske, enjeksiyon taraması ve **kural katmanı
  metnin tamamında**; **model** yalnızca ilk 2.000 karakteri (maskeli) görür. Model kanıtları modelin gördüğü
  metne karşı doğrulanır.
- **Kural 0 (katman v1.1):** model metnin tamamını göremediyse sonuç "düşük" olamaz → `KIRPILDI_DIKKAT` (belirsiz).
  `SistemCevabi.girdi_kirpildi` kullanıcıya da gösterilir.
- **Bedeli:** 2.000 karakteri aşan meşru mesajlar artık hep alarm (belirsiz). SMS/WhatsApp için nadir; e-posta zaten
  kapsam dışı (ADR-0006). OLTA/UCI FPR'si bu yüzden yükselir: bilinçli.

### 2. BYOK anahtarı (openai_compat v1.4)
- Hata metinleri anahtardan, `Bearer …` ve `sk-…` kalıplarından temizlenir (en kötü durum: sağlayıcı 401
  gövdesinde başlıkları aynen yankılar; test bunu sahte sunucuyla canlandırır).
- **Test bir açık buldu:** anahtar isim karıştırmalı bir alanda (`self.__anahtar`) tutuluyordu; `repr` gizliyordu
  ama `vars(arka_uc)` anahtarı **düz metin** gösteriyordu (hata ayıklama dökümleri, bazı log kütüphaneleri bunu
  yapar). Artık `_Gizli` sarmalayıcıda: `vars`/`str`/`repr` → `<gizli>`, `pickle` → hata.
- Test, anahtarı şu yerlerin hiçbirinde bulamamalı: repr, vars, hata, Iz, SistemCevabi, denetim satırı ve dosyası,
  ekran çıktısı.

### 3. Metinsiz denetim kaydı (`kalkan/denetim.py`)
Her analiz için bir JSONL satırı: zaman, trace_id, sürümler (kalkan/politika/katman), risk, tür, öneri kodu,
katman kaynağı, kural ve model riski, sinyal TÜRLERİ, kanıt SİNYALLERİ, girdi uzunluğu, kırpıldı mı, süre,
hata TÜRÜ ve `metin_ozeti` = HMAC-SHA256(tuz, ham)[:16].
- **İçermez:** mesaj, alıntılar, model ham çıktısı, hata metni (şema hatası model çıktısından parça taşıyabilir).
- Tuz `KALKAN_DENETIM_TUZ`'dan; yoksa süreç başına rastgele. Tuzsuz bir özet kısa SMS'ler için sözlükle geri
  çözülebilirdi.
- Dosya 0600. CLI: `python -m kalkan --denetim logs/denetim.jsonl "…"`. API (Adım 10) her istekte yazar.
- Test: adversarial ve kör setin her mesajı için, model mesajdan birebir alıntı yapsa bile denetim satırında
  mesajdan 10 karakterlik hiçbir pencere geçmemeli.

### 4. Kör saldırı seti (`data/adversarial/kor.yaml`, 20 örnek)
16 saldırı + 4 zor negatif. Saldırı türleri: kırpma (2), yeni enjeksiyon biçimleri (3: sahte "kalkan_cikti"
başlığı, "önceki kurallar iptal", sahte "Kalkan doğrulaması ✅"), homoglif (Kiril "а"), kelime içine sıfır
genişlikli boşluk, harfleri bölünmüş "k o d u", "[nokta]" ile gizlenmiş link, boşluklu/emoji'li kısa link,
BÜYÜK HARF + ASCII, İngilizce-Türkçe karışım, **ret satırlı sahte reklam** (politika v1.1'in reklam kuralını
atlatmaya çalışır), çok satırlı WhatsApp, markdown link (görünen resmi alan, giden sahte), alt alan hilesi.
Zor negatifler: meşru tek kullanımlık şifre, meşru kargo takip linki, meşru fatura, 2.000+ karakterlik meşru bülten.
**Kural:** bir kez ölçülür; sonuca bakarak kural, politika veya veri değiştirilirse o örnek `kor: false` olur.
kor_01/02/20 kırpma düzeltmesiyle birlikte yazıldığı için baştan `kor: false`. Sonuçlara ben de ölçümden önce bakmadım.

### Tahminler (kör set, ölçmeden önce)
| # | Tahmin |
|---|---|
| G1 | Sistem (katmanlı) kör sızıntı: **≤ 2 / 16**; en olası: kor_08 ("[nokta]"), kor_09 (boşluklu kısa link) |
| G2 | Kural tek başına: sızıntı **≥ 3** (bölünmüş kelime, gizlenmiş link, İngilizce karışım) |
| G3 | ft tek başına: sızıntı ≤ 2 ama zor negatiflerde ≥ 1 yanlış alarm |
| G4 | Sistem zor negatif: kor_17/18/19 temiz; kor_20 bilinçli belirsiz → yanlış alarm **1/4** |
| G5 | Mevcut adversarial (30) sistemde sızıntı 0 kalır |

### Sonuçlar (kör set, tek ölçüm · 2026-11-22)
| model | kör sızıntı (16 saldırı) | sızanlar | zor negatif yanlış alarm (4) |
|---|---|---|---|
| kural | 3 | kor_09 boşluklu kısa link, kor_10 BÜYÜK HARF+ASCII, kor_13 çok satırlı WhatsApp | kor_17 |
| TF-IDF | 1 | kor_12 ret satırlı sahte reklam | – |
| ft-v3 tek başına | 2 | kor_08 "[nokta]" link, kor_12 sahte reklam | kor_20 |
| **sistem (★ katmanlı)** | **2** | **kor_10, kor_13** | kor_17, kor_20 |

Mevcut adversarial (30) sistemde sızıntı **0** (G5 ✅). Keşif varyantları (karar ★'la): `veya` 0 sızıntı / 2 alarm,
`ikinci` (talep şartsız) 1 / 2.

**Karne:** G1 ◐ sayı tuttu (2 ≤ 2) ama adaylar yanlış: kor_08/09'u model ve kural birbirini tamamlayarak yakaladı,
sızanlar kor_10/13 · G2 ✅ (kural 3) · G3 ✅ (ft 2 sızıntı, 1 yanlış alarm) · G4 ❌ (2/4: meşru OTP kor_17'ye kural
alarm verdi) · G5 ✅.

**Kök nedenler (sızan iki örnek de aynı mekanizma):**
- Kural ikisini de "meşru" sandı: kor_10'da link yok, Türkçe karakter yok, "NUMARAYI ARAYIN" kanal sözlüğünde yok;
  kor_13'te tutar "TL"siz, talep fiili ("at", "gönder") yok, yalnızca IBAN var.
- Model ikisinde de dolandırıcılık dedi (ft tek başına ikisini de yakaladı), ama kanıtları arasında ödeme/kod/kimlik
  **talebi** yoktu → ★'ın talep şartı yükseltmeyi engelledi. Talep şartı golden'da FPR'yi korumak için konmuştu;
  bedeli burada görünür oldu.
- kor_13'te deterministik **IBAN sinyali vardı** ama politika IBAN'ı yalnızca reklam/kısa link yolunda kullanıyor:
  "meşru" denen ve IBAN içeren mesaj yükseltilmiyor. Sentetik verilerde meşru + IBAN **hiç yok** (test 0/54,
  doğrulama 0/36, eğitim 0/600): yani bu boşluk hiçbir ölçümde görünemezdi.
- kor_17 (meşru OTP → alarm): kuralın "şifre" kalıbı talep sayılıyor; "paylaşmayın" istisnası talep varsa devreye
  girmiyor. v2 modelin 8b'deki hatasının kural tarafındaki aynısı.

### Politika v1.2 (A yolu): IBAN kuralı
"Meşru/reklam" dense bile mesajda IBAN varsa → ORTA. kor_13 → `kor: false`. kor_10 ve kor_17 bilinçli olarak
düzeltilmedi (kör örneğe bakıp regex ayarlamak olurdu); ADR-0005 ekinde "bilinen zayıflık". Yeni kör örnekler:
kor_21 (karekodla ödeme, linksiz), kor_22 (telefonla kod isteyen "güvenlik birimi"), kor_24 (kripto adresine ücret).
kor_23 (arkadaş arası meşru IBAN) kuralın bedelini görmek için yazıldı → `kor: false`; alarm alması beklenir.

Tahminler (v1.2 ölçümünden önce): golden/doğrulama FPR **değişmez** (IBAN'lı meşru yok); kor_13 artık yakalanır;
kor_23 yanlış alarm alır; yeni kör örneklerden (kor_21/22/24) **en çok 1'i** sızar (en olası kor_21: link, IBAN,
talep fiili yok).

**Yan hata (bulundu ve düzeltildi): `yeniden_puanla` v1 katmanlı sonuçları bozdu.** v1.2'yi uygulamak için
çalıştırılan `make yeniden-puanla`, `sistem-*` ve `katmanli__*` dosyalarını katman mantığı olmadan, yalnızca model
politikasıyla yeniden puanladı (ör. katmanli__uci recall 0.767 → 0.625; sistem golden'da 33 risk değişti; metrikler
şans eseri aynı kaldı). Ayrıca eski veri sürümlü bir dosyada (zs-0.8b doğrulama) çöktü. v1.1: katmanli__* atlanır
(`make katmanli` üretir), sistem-* servisle aynı hatla puanlanır (bunun için sonuçlara `model_tur` eklendi; eski
dosyalar `risk_onceki`'den geri alınır), eski veri sürümlü dosyalar atlanır. Test: `test_yeniden_puanla_katmanli_servisle_ayni`.

**v1.2 sonuçları (kör set v1.1, 24 örnek; sistem gerçek llama-server ile):**
| model | sızıntı (19 saldırı) | sızanlar | zor negatif yanlış alarm (5) |
|---|---|---|---|
| kural (tür vekili, politikasız) | 3 | kor_09, kor_10, kor_13 | kor_17 |
| TF-IDF | 2 | kor_12, kor_24 | kor_23 |
| ft-v3 tek başına | 2 | kor_08, kor_12 | kor_20, kor_23 |
| **sistem (★, politika v1.2)** | **1** | **kor_10** (bilinen zayıflık) | kor_17 (bilinen), kor_20 (bilinçli), kor_23 (bilinçli) |

- golden ★ 0.905 / 1.000 / 0.018 ve doğrulama ★ **değişmedi** ✅ · adversarial sızıntı 0 ✅ · kor_13 artık yakalanıyor ✅.
- **Yeni kör örneklerin üçü de (kor_21 karekod, kor_22 telefonla kod, kor_24 kripto adresi) sistemde yakalandı**
  (tahmin: en çok 1 sızar → 0 sızdı ✅). Kural da üçünü tek başına yakaladı (sızanlar listesinde yoklar); TF-IDF
  kor_24'ü kaçırdı. Yani bu üç örnekte katmanlı yapı kurala bir şey eklemedi.
- kor_23 (arkadaş arası meşru IBAN) beklendiği gibi alarm aldı: v1.2'nin görünür bedeli.
- Kural satırı tür vekiliyle ölçülüyor (politika uygulanmaz); IBAN kuralı politikada olduğu için kural tek başına
  kor_13'ü hâlâ kaçırıyor gibi görünür, sistemde kural katmanı politikadan geçtiği için yakalanır.

**Adım 9 sonu, açık zayıflıklar (README "Sınırlar"a girecek):**
1. kor_10 türü: BÜYÜK HARF + ASCII, linksiz, "numarayı arayın" yönlendirmesi (kural sözlüğü kaçırıyor; model
   bulsa bile talep kanıtı alıntılamadığı için ★ yükseltmiyor).
2. kor_17 türü: meşru tek kullanımlık şifre bildirimi, kural "şifre" kelimesini talep sayıyor → yanlış alarm.
3. 2.000+ karakterlik meşru mesajlar ve IBAN içeren meşru mesajlar → bilinçli alarm (belirsiz/orta).
4. Kör setin 19 saldırısından 16'sı hâlâ kör (kor_01/02 kırpma kuralıyla, kor_13 v1.2'yi tetikledi); bir sonraki
   ayar turundan önce yeni kör örnek gerekir.

**Denetim satırı** (CLI örneği): mesajdan kelime yok; yalnızca sinyal türleri (`kisa_link`, `link`, `tutar`),
kanıt sinyalleri, uzunluk (48), HMAC özeti ✅.

İstek alan bir uç nokta henüz yok; API ile birlikte Adım 10'da (IP başına + toplam eşzamanlılık; llama-server
`-np 1` olduğu için kuyruk sınırı da).
