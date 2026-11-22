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
| kural | 0.887 | 0.896 | 0.975 ✅ | 0.000 ✅ | 1.000 ✅ | 0.713 | 1.000 | 0.800 | 2.100 | 0.000 |
| tfidf | 0.689 | 0.707 | 1.000 ✅ | 0.000 ✅ | — | — | 1.000 | 0.800 | 1.000 | 0.000 |
| zs-0.8b | 0.128 | 0.195 | 1.000 ✅ | 1.000 ❌ | 0.482 ❌ | 0.106 | 1.000 | 1132.900 | 1958.500 | 0.000 |
| zs-2b | 0.235 | 0.323 | 1.000 ✅ | 0.426 ❌ | 0.767 ❌ | 0.021 | 1.000 | 416.900 | 1015.800 | 0.000 |
| gpt-5.4-mini | 0.904 | 0.909 | 1.000 ✅ | 0.000 ✅ | 0.964 ✅ | 0.770 | 1.000 | 1161.200 | 1385.900 | 1.199 |
| ft-0.8b-v2-Q8_0 | 0.507 | 0.552 | 1.000 ✅ | 0.296 ❌ | 0.970 ✅ | 0.793 | 1.000 | 1078.700 | 1338.500 | 0.000 |
| ft-0.8b-v3-Q8_0 | 0.552 | 0.609 | 1.000 ✅ | 0.018 ✅ | 0.970 ✅ | 0.783 | 1.000 | 1301.000 | 1613.800 | 0.000 |
| katmanli | 0.905 | 0.909 | 1.000 ✅ | 0.018 ✅ | 1.000 ✅ | 0.785 | 1.000 | 1301.000 | 1613.800 | 0.000 |
| sistem-v3-Q8_0 | 0.905 | 0.909 | 1.000 ✅ | 0.018 ✅ | 0.970 ✅ | 0.783 | 1.000 | 1050.700 | 1264.300 | 0.000 |


## Doğrulama (ayar seti) ↔ golden farkı
Büyük düşüş = doğrulama setine aşırı uyum.

| model | doğrulama makro-F1 | golden makro-F1 | fark |
|---|---|---|---|
| kural | 0.722 | 0.887 | +0.165 |
| tfidf | 0.822 | 0.689 | -0.133 |
| zs-0.8b | 0.131 | 0.128 | -0.003 |
| zs-2b | 0.204 | 0.235 | +0.032 |
| ft-0.8b-v2-Q8_0 | 0.594 | 0.507 | -0.087 |
| ft-0.8b-v3-Q8_0 | 0.573 | 0.552 | -0.020 |
| katmanli | 0.758 | 0.905 | +0.147 |
| sistem-v3-Q8_0 | 0.758 | 0.905 | +0.147 |


## Adversarial (30 örnek)
Vekil ölçüt (politika kodu Adım 5'te): dolandırıcılık dışı tür = düşük risk.

| model | düşük risk sızıntısı | sızan örnekler | zor negatif yanlış alarm | tür kabul |
|---|---|---|---|---|
| kural | 1 ❌ | adv_23 (kanal) | 2/7 | 0.833 |
| tfidf | 3 ❌ | adv_10 (homoglyph), adv_17 (hibrit), adv_19 (hibrit) | 3/7 | 0.833 |
| zs-0.8b | 0 ✅ | — | 7/7 | 0.167 |
| zs-2b | 0 ✅ | — | 6/7 | 0.200 |
| gpt-5.4-mini | 0 ✅ | — | 0/7 | 0.967 |
| ft-0.8b-v2-Q8_0 | 0 ✅ | — | 6/7 | 0.400 |
| ft-0.8b-v3-Q8_0 | 1 ❌ | adv_18 (hibrit) | 3/7 | 0.367 |
| katmanli | 0 ✅ | — | 3/7 | 0.800 |
| sistem-v3-Q8_0 | 0 ✅ | — | 3/7 | 0.800 |


## Dış setler (ikili: dolandırıcılık mı?)
OLTA-TR sentetik oltalama e-postası, UCI gerçek spam/normal e-posta. İkisi de e-posta; bizim veri SMS. Alan kayması bekleniyor.

| model | OLTA n | OLTA recall | OLTA meşru FPR | UCI n | UCI spam→alarm | UCI normal→alarm |
|---|---|---|---|---|---|---|
| kural | 18305 | 0.197 | 0.195 | 825 | 0.395 | 0.321 |
| tfidf | 18305 | 0.708 | 0.543 | 825 | 0.745 | 0.802 |
| zs-0.8b | 300 | 1.000 | 1.000 | 300 | 1.000 | 0.967 |
| zs-2b | 300 | 0.830 | 0.712 | 300 | 0.958 | 0.856 |
| gpt-5.4-mini | 50 | 0.867 | 0.500 | — | — | — |
| ft-0.8b-v2-Q8_0 | 300 | 0.956 | 0.924 | 300 | 1.000 | 0.994 |
| ft-0.8b-v3-Q8_0 | 300 | 0.995 | 0.983 | 300 | 0.925 | 0.978 |
| katmanli | 300 | 0.665 | 0.542 | 300 | 0.558 | 0.511 |
| sistem-v3-Q8_0 | 300 | 0.665 | 0.542 | 300 | 0.558 | 0.511 |


## En çok karışan tür çiftleri (golden)

- **kural**: oyun_hesap_skin → yakin_taklidi (13), gorev_is_ilani → sahte_kargo_gumruk (10), gorev_is_ilani → mesru_islem (5), yakin_taklidi → kurum_taklidi (1)
- **tfidf**: yatirim_vip_grup → gorev_is_ilani (27), yasa_disi_bahis → gorev_is_ilani (14), oyun_hesap_skin → odul_kampanya (13), sahte_kargo_gumruk → odul_kampanya (13)
- **zs-0.8b**: sahte_kamu_gorevlisi → yakin_taklidi (20), oyun_hesap_skin → odul_kampanya (17), mesru_islem → sahte_kargo_gumruk (16), odul_kampanya → sahte_kargo_gumruk (15)
- **zs-2b**: gorev_is_ilani → sahte_kargo_gumruk (27), yakin_taklidi → sahte_kargo_gumruk (26), kurum_taklidi → sahte_kargo_gumruk (24), odul_kampanya → sahte_kargo_gumruk (21)
- **gpt-5.4-mini**: oyun_hesap_skin → odul_kampanya (14), yatirim_vip_grup → odul_kampanya (7), yatirim_vip_grup → gorev_is_ilani (5), yatirim_vip_grup → reklam_spam (1)
- **ft-0.8b-v2-Q8_0**: yatirim_vip_grup → gorev_is_ilani (27), sahte_kargo_gumruk → sahte_kamu_gorevlisi (13), oyun_hesap_skin → odul_kampanya (13), kurum_taklidi → oyun_hesap_skin (10)
- **ft-0.8b-v3-Q8_0**: yatirim_vip_grup → gorev_is_ilani (23), yasa_disi_bahis → gorev_is_ilani (14), sahte_kargo_gumruk → kurum_taklidi (14), oyun_hesap_skin → odul_kampanya (12)
- **katmanli**: oyun_hesap_skin → yakin_taklidi (13), gorev_is_ilani → sahte_kargo_gumruk (10), mesru_islem → odul_kampanya (1), yakin_taklidi → kurum_taklidi (1)
- **sistem-v3-Q8_0**: oyun_hesap_skin → yakin_taklidi (13), gorev_is_ilani → sahte_kargo_gumruk (10), mesru_islem → odul_kampanya (1), yakin_taklidi → kurum_taklidi (1)


## Gürültü tipine göre doğruluk (golden)

| model | (yok) | ascii | bosluk | buyuk_harf | emoji | yazim |
|---|---|---|---|---|---|---|
| kural | 0.901 | 0.917 | 0.829 | 0.944 | 1.000 | 0.830 |
| tfidf | 0.730 | 0.625 | 0.771 | 0.778 | 0.583 | 0.774 |
| zs-0.8b | 0.206 | 0.236 | 0.257 | 0.056 | 0.208 | 0.151 |
| zs-2b | 0.319 | 0.306 | 0.400 | 0.278 | 0.250 | 0.321 |
| gpt-5.4-mini | 0.915 | 0.931 | 0.886 | 1.000 | 0.833 | 0.868 |
| ft-0.8b-v2-Q8_0 | 0.603 | 0.458 | 0.600 | 0.556 | 0.458 | 0.547 |
| ft-0.8b-v3-Q8_0 | 0.695 | 0.472 | 0.571 | 0.444 | 0.583 | 0.642 |
| sistem-v3-Q8_0 | 0.901 | 0.917 | 0.857 | 0.944 | 1.000 | 0.906 |


<details><summary>Sürüm izleri</summary>

- `kural/adversarial`: git ef617cc · veri 539ec5edf4cc57b7 · 2026-11-22T11:44:33
- `kural/dogrulama`: git ef617cc · veri d2b097bf4bf12685 · 2026-11-22T11:44:33
- `kural/golden`: git ef617cc · veri 2e46892225886536 · 2026-11-22T11:44:33
- `kural/olta`: git ef617cc · veri 43fcfc17d8b1b7d9 · 2026-11-22T11:45:40
- `kural/uci`: git ef617cc · veri 0000d324844a291a · 2026-11-22T11:45:47
- `tfidf/adversarial`: git ef617cc · veri 539ec5edf4cc57b7 · 2026-11-22T11:45:50
- `tfidf/dogrulama`: git ef617cc · veri d2b097bf4bf12685 · 2026-11-22T11:45:50
- `tfidf/golden`: git ef617cc · veri 2e46892225886536 · 2026-11-22T11:45:50
- `tfidf/olta`: git ef617cc · veri 43fcfc17d8b1b7d9 · 2026-11-22T11:46:33
- `tfidf/uci`: git ef617cc · veri 0000d324844a291a · 2026-11-22T11:46:37
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
- `ft-0.8b-v2-Q8_0/adversarial`: git 7080361 · veri 539ec5edf4cc57b7 · 2026-11-22T11:20:59
- `ft-0.8b-v2-Q8_0/dogrulama`: git 7080361 · veri d2b097bf4bf12685 · 2026-11-22T11:20:30
- `ft-0.8b-v2-Q8_0/golden`: git 7080361 · veri 2e46892225886536 · 2026-11-22T11:16:50
- `ft-0.8b-v2-Q8_0/olta`: git 7080361 · veri 43fcfc17d8b1b7d9 · 2026-11-22T11:28:02
- `ft-0.8b-v2-Q8_0/uci`: git 7080361 · veri 0000d324844a291a · 2026-11-22T11:36:25
- `ft-0.8b-v3-Q8_0/adversarial`: git 3929225 · veri 539ec5edf4cc57b7 · 2026-11-22T14:26:46
- `ft-0.8b-v3-Q8_0/dogrulama`: git 3929225 · veri d2b097bf4bf12685 · 2026-11-22T14:26:26
- `ft-0.8b-v3-Q8_0/golden`: git 3929225 · veri 2e46892225886536 · 2026-11-22T14:22:31
- `ft-0.8b-v3-Q8_0/olta`: git 3929225 · veri 43fcfc17d8b1b7d9 · 2026-11-22T14:35:04
- `ft-0.8b-v3-Q8_0/uci`: git 3929225 · veri 0000d324844a291a · 2026-11-22T14:43:50
- `katmanli/adversarial`: git 3929225 · veri 539ec5edf4cc57b7 · 2026-11-22T14:26:46
- `katmanli/dogrulama`: git 3929225 · veri d2b097bf4bf12685 · 2026-11-22T14:26:26
- `katmanli/golden`: git 3929225 · veri 2e46892225886536 · 2026-11-22T14:22:31
- `katmanli/olta`: git 3929225 · veri 43fcfc17d8b1b7d9 · 2026-11-22T14:35:04
- `katmanli/uci`: git 3929225 · veri 0000d324844a291a · 2026-11-22T14:43:50
- `sistem-v3-Q8_0/adversarial`: git 299b1e7 · veri 539ec5edf4cc57b7 · 2026-11-22T17:10:55
- `sistem-v3-Q8_0/dogrulama`: git 299b1e7 · veri d2b097bf4bf12685 · 2026-11-22T17:10:38
- `sistem-v3-Q8_0/golden`: git 299b1e7 · veri 2e46892225886536 · 2026-11-22T17:07:30
- `sistem-v3-Q8_0/olta`: git 299b1e7 · veri 43fcfc17d8b1b7d9 · 2026-11-22T17:18:20
- `sistem-v3-Q8_0/uci`: git 299b1e7 · veri 0000d324844a291a · 2026-11-22T17:26:32
</details>
<!-- OTOMATIK:SON -->
