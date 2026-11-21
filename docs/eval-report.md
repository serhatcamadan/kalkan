# Kalkan — değerlendirme raporu

Elle yazılan yorumlar bu bölümün DIŞINA yazılır; `python -m eval.report` yalnızca aradaki kısmı yeniler.

## Yorum (elle, Adım 4)
- İkili soru ("dolandırıcılık mı?") iki taban çizgisinde de sentetik golden'da eşikleri geçiyor. Tür sorusunda TF-IDF
  yeni şablonlara genelleyemiyor (0.49). Kural modeli 0.89, ama doğrulamaya göre ayarlandığı için iyimser.
- Kanıt üretebilen tek taban çizgisi kural modeli. LLM'lerden beklenen: tür makro-F1'de kuralı geçmek ve kanıt
  eşleşmesinde 0.71'in üstüne çıkmak, adversarial sızıntıyı 0'a indirmek.
- **Dış set uyarısı:** OLTA-TR'de kural modeli ayırt edemiyor (recall 0.20 ≈ FPR 0.19), TF-IDF meşru e-postaların
  yarısına alarm veriyor (FPR 0.51). Sentetik golden'daki başarı gerçek dağılıma taşınmıyor. Model seçiminde dış set
  sonuçları golden kadar ağırlık taşıyacak.
- **Zero-shot (Adım 5):** 0.8B her şeye alarm veriyor (golden meşru FPR 1.00), 2B tür ayıramıyor (makro-F1 0.24) ve
  dış sette TF-IDF'in altında. Küçük model talimatla değil örnekle öğrenmeli → fine-tune (Adım 7).
- **gpt-5.4-mini (Adım 6):** golden 0.905, meşru FPR 0, kanıt eşleşme 0.77 → sorun istem değil ölçekti. OLTA'da 0.25:
  kaçan oltalamalar meşru bülten gibi yazılmış, farkı bağlantı yaratıyor → metin-yalnız yaklaşımın tavanı (sınırlama).
- Ayrıntı ve tahmin karneleri: `docs/adim-04-eval.md`, `docs/adim-05-pipeline.md`, `docs/adim-06-gpt.md`.

<!-- OTOMATIK:BAS -->
## Golden test (297 örnek, şablon ve marka ayrık)

| model | makro-F1 (tür) | doğruluk | dol. recall | meşru FPR | kanıt geçerlilik (kapı öncesi) | kanıt eşleşme F1 | JSON geçerlilik | p50 ms | p95 ms | $/1000 |
|---|---|---|---|---|---|---|---|---|---|---|
| kural | 0.887 | 0.896 | 0.975 ✅ | 0.000 ✅ | 1.000 ✅ | 0.713 | 1.000 | 0.800 | 2.200 | 0.000 |
| tfidf | 0.491 | 0.525 | 1.000 ✅ | 0.000 ✅ | — | — | 1.000 | 0.700 | 0.800 | 0.000 |
| zs-0.8b | 0.128 | 0.195 | 1.000 ✅ | 1.000 ❌ | 0.482 ❌ | 0.106 | 1.000 | 1132.900 | 1958.500 | 0.000 |
| zs-2b | 0.235 | 0.323 | 1.000 ✅ | 0.426 ❌ | 0.767 ❌ | 0.021 | 1.000 | 416.900 | 1015.800 | 0.000 |
| gpt-5.4-mini | 0.904 | 0.909 | 1.000 ✅ | 0.000 ✅ | 0.964 ✅ | 0.770 | 1.000 | 1161.200 | 1385.900 | 1.199 |


## Doğrulama (ayar seti) ↔ golden farkı
Büyük düşüş = doğrulama setine aşırı uyum.

| model | doğrulama makro-F1 | golden makro-F1 | fark |
|---|---|---|---|
| kural | 0.990 | 0.887 | -0.103 |
| tfidf | 0.716 | 0.491 | -0.225 |
| zs-0.8b | 0.131 | 0.128 | -0.003 |
| zs-2b | 0.204 | 0.235 | +0.032 |


## Adversarial (30 örnek)
Vekil ölçüt (politika kodu Adım 5'te): dolandırıcılık dışı tür = düşük risk.

| model | düşük risk sızıntısı | sızan örnekler | zor negatif yanlış alarm | tür kabul |
|---|---|---|---|---|
| kural | 1 ❌ | adv_23 (kanal) | 2/7 | 0.833 |
| tfidf | 2 ❌ | adv_17 (hibrit), adv_19 (hibrit) | 3/7 | 0.900 |
| zs-0.8b | 0 ✅ | — | 7/7 | 0.167 |
| zs-2b | 0 ✅ | — | 6/7 | 0.200 |
| gpt-5.4-mini | 0 ✅ | — | 0/7 | 0.967 |


## Dış setler (ikili: dolandırıcılık mı?)
OLTA-TR sentetik oltalama e-postası, UCI gerçek spam/normal e-posta. İkisi de e-posta; bizim veri SMS. Alan kayması bekleniyor.

| model | OLTA n | OLTA recall | OLTA meşru FPR | UCI n | UCI spam→alarm | UCI normal→alarm |
|---|---|---|---|---|---|---|
| kural | 18305 | 0.197 | 0.195 | 825 | 0.395 | 0.321 |
| tfidf | 18305 | 0.721 | 0.510 | 825 | 0.708 | 0.758 |
| zs-0.8b | 300 | 1.000 | 1.000 | 300 | 1.000 | 0.967 |
| zs-2b | 300 | 0.830 | 0.712 | 300 | 0.958 | 0.856 |
| gpt-5.4-mini | 50 | 0.867 | 0.500 | — | — | — |


## En çok karışan tür çiftleri (golden)

- **kural**: oyun_hesap_skin → yakin_taklidi (13), gorev_is_ilani → sahte_kargo_gumruk (10), gorev_is_ilani → mesru_islem (5), yakin_taklidi → kurum_taklidi (1)
- **tfidf**: yatirim_vip_grup → gorev_is_ilani (26), odul_kampanya → sahte_kargo_gumruk (22), yasa_disi_bahis → yatirim_vip_grup (14), oyun_hesap_skin → yakin_taklidi (13)
- **zs-0.8b**: sahte_kamu_gorevlisi → yakin_taklidi (20), oyun_hesap_skin → odul_kampanya (17), mesru_islem → sahte_kargo_gumruk (16), odul_kampanya → sahte_kargo_gumruk (15)
- **zs-2b**: gorev_is_ilani → sahte_kargo_gumruk (27), yakin_taklidi → sahte_kargo_gumruk (26), kurum_taklidi → sahte_kargo_gumruk (24), odul_kampanya → sahte_kargo_gumruk (21)
- **gpt-5.4-mini**: oyun_hesap_skin → odul_kampanya (14), yatirim_vip_grup → odul_kampanya (7), yatirim_vip_grup → gorev_is_ilani (5), yatirim_vip_grup → reklam_spam (1)


## Gürültü tipine göre doğruluk (golden)

| model | (yok) | ascii | bosluk | buyuk_harf | emoji | yazim |
|---|---|---|---|---|---|---|
| kural | 0.901 | 0.917 | 0.829 | 0.944 | 1.000 | 0.830 |
| tfidf | 0.567 | 0.528 | 0.457 | 0.444 | 0.417 | 0.528 |
| zs-0.8b | 0.206 | 0.236 | 0.257 | 0.056 | 0.208 | 0.151 |
| zs-2b | 0.319 | 0.306 | 0.400 | 0.278 | 0.250 | 0.321 |
| gpt-5.4-mini | 0.915 | 0.931 | 0.886 | 1.000 | 0.833 | 0.868 |


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
- `zs-0.8b/adversarial`: git 79266c7 · veri 539ec5edf4cc57b7 · 2026-11-20T22:50:34
- `zs-0.8b/dogrulama`: git 79266c7 · veri a70861c206cda3eb · 2026-11-20T22:49:59
- `zs-0.8b/golden`: git 79266c7 · veri 2e46892225886536 · 2026-11-20T22:45:43
- `zs-0.8b/olta`: git 79266c7 · veri 43fcfc17d8b1b7d9 · 2026-11-20T23:01:39
- `zs-0.8b/uci`: git 79266c7 · veri 0000d324844a291a · 2026-11-20T23:12:58
- `zs-2b/adversarial`: git 79266c7 · veri 539ec5edf4cc57b7 · 2026-11-20T23:20:41
- `zs-2b/dogrulama`: git 79266c7 · veri a70861c206cda3eb · 2026-11-20T23:20:25
- `zs-2b/golden`: git 79266c7 · veri 2e46892225886536 · 2026-11-20T23:18:11
- `zs-2b/olta`: git 79266c7 · veri 43fcfc17d8b1b7d9 · 2026-11-20T23:23:40
- `zs-2b/uci`: git 79266c7 · veri 0000d324844a291a · 2026-11-20T23:29:24
- `gpt-5.4-mini/adversarial`: git d195a4a · veri 539ec5edf4cc57b7 · 2026-11-21T12:56:24
- `gpt-5.4-mini/golden`: git d195a4a · veri 2e46892225886536 · 2026-11-21T12:55:51
- `gpt-5.4-mini/olta`: git d195a4a · veri 43fcfc17d8b1b7d9 · 2026-11-21T12:57:18
</details>
<!-- OTOMATIK:SON -->
