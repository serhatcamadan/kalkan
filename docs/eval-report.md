# Kalkan — değerlendirme raporu

Elle yazılan yorumlar bu bölümün DIŞINA yazılır; `python -m eval.report` yalnızca aradaki kısmı yeniler.

## Yorum (elle, Adım 4)
- İkili soru ("dolandırıcılık mı?") iki taban çizgisinde de sentetik golden'da eşikleri geçiyor. Tür sorusunda TF-IDF
  yeni şablonlara genelleyemiyor (0.49). Kural modeli 0.89, ama doğrulamaya göre ayarlandığı için iyimser.
- Kanıt üretebilen tek taban çizgisi kural modeli. LLM'lerden beklenen: tür makro-F1'de kuralı geçmek ve kanıt
  eşleşmesinde 0.71'in üstüne çıkmak, adversarial sızıntıyı 0'a indirmek.
- Ayrıntı ve tahmin karnesi: `docs/adim-04-eval.md`.

<!-- OTOMATIK:BAS -->
## Golden test (297 örnek, şablon ve marka ayrık)

| model | makro-F1 (tür) | doğruluk | dol. recall | meşru FPR | kanıt geçerlilik (kapı öncesi) | kanıt eşleşme F1 | JSON geçerlilik | p50 ms | p95 ms | $/1000 |
|---|---|---|---|---|---|---|---|---|---|---|
| kural | 0.887 | 0.896 | 0.975 ✅ | 0.000 ✅ | 1.000 ✅ | 0.713 | 1.000 | 0.800 | 2.200 | 0.000 |
| tfidf | 0.491 | 0.525 | 1.000 ✅ | 0.000 ✅ | — | — | 1.000 | 0.700 | 0.800 | 0.000 |


## Doğrulama (ayar seti) ↔ golden farkı
Büyük düşüş = doğrulama setine aşırı uyum.

| model | doğrulama makro-F1 | golden makro-F1 | fark |
|---|---|---|---|
| kural | 0.990 | 0.887 | -0.103 |
| tfidf | 0.716 | 0.491 | -0.225 |


## Adversarial (30 örnek)
Vekil ölçüt (politika kodu Adım 5'te): dolandırıcılık dışı tür = düşük risk.

| model | düşük risk sızıntısı | sızan örnekler | zor negatif yanlış alarm | tür kabul |
|---|---|---|---|---|
| kural | 1 ❌ | adv_23 (kanal) | 2/7 | 0.833 |
| tfidf | 2 ❌ | adv_17 (hibrit), adv_19 (hibrit) | 3/7 | 0.900 |


## Dış setler (ikili: dolandırıcılık mı?)
OLTA-TR sentetik oltalama e-postası, UCI gerçek spam/normal e-posta. İkisi de e-posta; bizim veri SMS. Alan kayması bekleniyor.

| model | OLTA n | OLTA recall | OLTA meşru FPR | UCI n | UCI spam→alarm | UCI normal→alarm |
|---|---|---|---|---|---|---|
| kural | 18305 | 0.197 | 0.195 | 825 | 0.395 | 0.321 |
| tfidf | 18305 | 0.721 | 0.510 | 825 | 0.708 | 0.758 |


## En çok karışan tür çiftleri (golden)

- **kural**: oyun_hesap_skin → yakin_taklidi (13), gorev_is_ilani → sahte_kargo_gumruk (10), gorev_is_ilani → mesru_islem (5), yakin_taklidi → kurum_taklidi (1)
- **tfidf**: yatirim_vip_grup → gorev_is_ilani (26), odul_kampanya → sahte_kargo_gumruk (22), yasa_disi_bahis → yatirim_vip_grup (14), oyun_hesap_skin → yakin_taklidi (13)


## Gürültü tipine göre doğruluk (golden)

| model | (yok) | ascii | bosluk | buyuk_harf | emoji | yazim |
|---|---|---|---|---|---|---|
| kural | 0.901 | 0.917 | 0.829 | 0.944 | 1.000 | 0.830 |
| tfidf | 0.567 | 0.528 | 0.457 | 0.444 | 0.417 | 0.528 |


<details><summary>Sürüm izleri</summary>

- `kural/adversarial`: git 284aa14 · veri 539ec5edf4cc57b7 · 2026-11-20T22:10:05
- `kural/dogrulama`: git 284aa14 · veri a70861c206cda3eb · 2026-11-20T22:10:05
- `kural/golden`: git 284aa14 · veri 2e46892225886536 · 2026-11-20T22:10:05
- `kural/olta`: git 284aa14 · veri 43fcfc17d8b1b7d9 · 2026-11-20T22:11:12
- `kural/uci`: git 284aa14 · veri 0000d324844a291a · 2026-11-20T22:11:18
- `tfidf/adversarial`: git 284aa14 · veri 539ec5edf4cc57b7 · 2026-11-20T22:11:21
- `tfidf/dogrulama`: git 284aa14 · veri a70861c206cda3eb · 2026-11-20T22:11:21
- `tfidf/golden`: git 284aa14 · veri 2e46892225886536 · 2026-11-20T22:11:21
- `tfidf/olta`: git 284aa14 · veri 43fcfc17d8b1b7d9 · 2026-11-20T22:12:04
- `tfidf/uci`: git 284aa14 · veri 0000d324844a291a · 2026-11-20T22:12:08
</details>
<!-- OTOMATIK:SON -->
