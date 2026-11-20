# Veri kartı — Kalkan sentetik Türkçe dolandırıcılık mesajları · v1 · 2026-11-20

## Özet
| Bölüm | Örnek | Şablon | Marka havuzu | Amaç |
|---|---|---|---|---|
| egitim | 1.496 | 44 | 16 | Fine-tune (Adım 7) |
| dogrulama | 198 | 11 | 7 | Model/epoch seçimi |
| test | 297 | 22 | 11 | Golden set (150'si elle incelenecek) |
| adversarial | 30 | elle | 3 (ayrı) | Saldırı ve zor negatif ölçümü, eğitimde YOK |

11 tür, eğitimde her tür 136 örnek (dengeli). Üretim deterministik: `python tools/veri_uret.py` (tohum 20261120).

## Nasıl üretildi?
1. **77 şablon** (`data/templates/sablonlar.yaml`), tür başına 7: 4 eğitim, 1 doğrulama, 2 test. `{a|b}` varyasyonları ve
   `{SLOT}` doldurma (tutar, süre, link, IBAN, telefon, ad…).
2. **Kanıt önce:** Kanıtlar şablonda `⟦sinyal:metin⟧` ile işaretli. Gürültü işaretlere dokunmaz, bu yüzden alıntı mesajda
   daima birebir geçer. Hedef çıktı, MASKELİ girdiye göre üretilir ve şema (≤3 kanıt, ≤80 karakter) ile doğrulanır.
3. **Gürültü:** Türkçe karakter kaybı (~%25, dolandırıcı SMS'lerinde yaygın), yazım hatası (~%15, yalnızca düz kelimelerde;
   link ve sayılar bozulmaz), çift boşluk (~%10), BÜYÜK HARF (~%8), emoji (~%8).
4. **Maskeleme:** `model_girdisi` = kanonik metin + PII/OTP maskesi. Model ham telefon/IBAN/kod görmez.

## Sızıntı önlemleri ve ölçümü
- Bölme **şablon bazlı**. Her bölümün **ayrı marka havuzu** var. Ortak şablon/marka/metin: 0 (test ile denetleniyor).
- Kelime 8-gram örtüşmesi test→eğitim: **%0.0**. Not: bu, testin "kolay" değil, aksine fazla temiz olduğunu da gösterir.
  Gerçek dünyada dolandırıcılar ortak kalıplar kullanır. Bu yüzden dış set (OLTA-TR, UCI) ayrıca ölçülecek.

## Kişisel veri
- Gerçek kişisel veri **yok**. Adlar yaygın Türkçe ilk adlardan rastgele, soyadı yok.
- Telefonlar `0599 xxx xx xx` aralığından üretilir. IBAN'lar banka kodu `99999` ile ve geçerli mod-97 ile üretilir.
  Bu aralıkların tahsisli olmaması **amaçlanmıştır, doğrulanmamıştır**. Model girdisinde zaten maskelidir.
- Kurum ve marka adları kurgusaldır (Mavibank, Kuzeykart, Sedirbank…). Gerçek bir kurumla benzerlik kasıtlı değildir.
  Kamu rolleri ("Savcılık", "MASAK", "Emniyet") genel unvan olarak geçer, çünkü dolandırıcılar tam olarak bunları taklit eder.

## Dış setler (repoya konmaz, `data/external/download.py`)
| Set | Lisans | İçerik | Dikkat |
|---|---|---|---|
| OLTA-TR (Zenodo, 10.5281/zenodo.19472163) | CC BY 4.0 | 18.305 sentetik e-posta (11.082 oltalama / 7.223 meşru), LLM üretimi | Oltalamaların ~%13'ü **gerçek zararlı URL** içeriyor → indirmede defang |
| UCI Turkish Spam V01 (10.24432/C5WG7F) | CC BY 4.0 | 826 e-posta (330 spam / 496 normal) | **Gerçek kişisel hesaplardan** toplanmış → yalnızca toplu metrik, örnek metin yayımlanmaz |
| Kaggle TurkishSMSCollection | — | | **KULLANILMIYOR**: gerçek kişilerin SMS'leri, lisans belirsiz |

İki dış set de **e-posta**. Bizim veri SMS/WhatsApp kısalığında. Alan kayması beklenir ve raporlanacak.

## Bilinen sınırlamalar
1. Şablon kaynaklı veri iyimser skor verir. Şablon bölmesi ve dış set bunu ölçmek için var, ortadan kaldırmaz.
2. Taksonomide **"kişisel/diğer"** sınıfı yok. "Anne eve geçtim" gibi sıradan bir mesaj (adv_30) hiçbir türe tam uymuyor.
   Şimdilik dolandırıcılık dışı türlerden biri kabul ediliyor. Açık konu.
3. Yazıyla tutarlar ("4bin", "beş yüz") deterministik olarak tanınmıyor (adv_16).
4. Dengeli sınıf dağılımı gerçek dünyayı yansıtmaz (gerçekte meşru mesaj çok daha fazla). Meşru FPR ayrıca raporlanacak.
5. Yerel LLM ile parafraz (yol haritasındaki qwen3.5:4b adımı) bu sürümde **yapılmadı**. Önce şablon verisiyle
   baseline ölçülecek (Adım 4–6). Fark gerekirse v2'de parafraz eklenecek.
