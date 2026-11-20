# Adım 2 — Taksonomi, şema, sinyaller, PII · v1 · 2026-11-19

## Ne yapıldı, neden?
| Dosya | Görev | Adım 1'den gelen gerekçe |
|---|---|---|
| `data/taxonomy.yaml` | 11 tür, 11 sinyal, karışan tür çiftleri ve ayırt edici kural, kurgusal markalar | Zero-shot model sinyal etiketlerini karıştırıyordu → net tanım |
| `kalkan/schema.py` | `ModelCiktisi` (kanıt önce, en fazla 3 kanıt, alıntı ≤ 80 karakter, kompakt JSON) · `SistemCevabi` ("güvenli" yasak) | VPS'te gecikme = üretilen token. 96 token'da cevaplar kesiliyordu. |
| `kalkan/normalize.py` | Kanonik metin + uzunluk koruyan görünümler (tr_kucuk, kucuk, ascii, iskelet) | Kanıt kapısı ve vurgulama tek bir ofset sistemine muhtaç |
| `kalkan/signals.py` | Link (defang dahil), kısa link, punycode, benzer/marka içeren alan adı, IBAN, tutar, OTP, meşru uyarı, gizlilik ifadesi | Model alıntıları %64–88 birebir veriyordu → modelden bağımsız kanıt katmanı |
| `kalkan/pii.py` | IBAN (mod-97), KART (Luhn), TCKN (kontrol haneleri), TEL, EPOSTA, OTP maskeleme + maskeli→kanonik ofset çevirici | BYOK'ta metin dışarı çıkıyor |
| `tests/` | 52 birim testi | |
| `tools/token_olc.py` | 👀 Çıktı biçimlerinin token sayısı | Kompakt biçimin kazancını ölçmek |

## Tahminler (kod yazılmadan önce)
| # | Tahmin | Sonuç |
|---|---|---|
| P1 | Python'un `"İ".lower()` sonucu 2 karakter; düz `.lower()` ofsetleri kaydırır | ✅ Testle kanıtlandı (`test_buyuk_I_noktali_tuzagi`) |
| P2 | Rastgele 11 haneli sayıların ~%1'i TCKN kontrolünden geçer (kontrol hanesi 1/100) | ✅ 20.000 örnekte %0.5–1.5 bandında |
| P3 | Kompakt JSON + kısa alıntı, girintili biçime göre ≥ %35 daha az token | ⏳ `tools/token_olc.py` ile ölçülecek (karakterde girintili 348 → kompakt 258, %26) |
| P4 | İlk taslakta en az bir sinyal anlamca yanlış çıkar (Türkçe yüzey benzerliği) | ✅ Aşağıda, bulgu 1 |

## Bulgular (geliştirirken)
1. **Zıt anlamlı iki ifade aynı sinyale düşüyordu.** "Bu kodu kimseyle **paylaşmayın**" (meşru banka uyarısı) ile
   "kimseye **söyleme**" (dolandırıcının gizlilik baskısı) ilk taslakta aynı `paylasma_uyarisi` sinyalini üretiyordu.
   Bu, meşru-gibi işaretini dolandırıcılığa eklemek demek. Ayrıldı: `paylasma_uyarisi` (kod/şifre bağlamı şart) ve
   `gizlilik_ifadesi`. Regresyon testi eklendi.
2. **Canlı OTP sızıntısı.** Kullanıcı gerçek bir doğrulama kodunu yapıştırırsa kod maskelenmeden modele, BYOK'ta
   da dış sağlayıcıya gidiyordu. Ayrıca sinyal değerine de yazılıyordu. Artık `[OTP]` ile maskeleniyor, sinyal
   değerlerinde rakamlar `*` oluyor.
3. `rnavibank` (rn ≈ m) ve Kiril `а` içeren `mаvibank` "marka içeriyor" değil **taklit** sayılmalı: harfiyen içerme
   ve görsel iskelet ayrı kontrol ediliyor (`marka_iceren_yabanci` ve `benzer_alan_adi`).

## Bilinçli sınırlar
- Tutar yalnızca birimle (TL, ₺, lira) tanınır. "5 bin", "beş yüz" gibi yazıyla tutarlar v2.
- Telefon kalıbı TR odaklı. Yabancı numaralar maskelenmez (veri kartında not edilecek).
- `resmi_alan_adi` yalnızca bilgi verir. Bir mesajın resmi alan adı içermesi onu meşru YAPMAZ; politika kodu bunu
  tek başına güven gerekçesi olarak kullanmayacak.
