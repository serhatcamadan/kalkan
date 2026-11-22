# Adım 8 — fine-tune modeli GGUF'a, parite ve tam sistem ölçümü · v1 · 2026-11-21

## Amaç
Adım 7'de seçilen `ft-0.8b-v2-it600` adaptörünü dağıtılabilir biçime (GGUF Q4_K_M, llama-server; ADR-0001/0002)
çevirip iki soruyu cevaplamak:
1. **Parite (H4):** Dönüşüm modeli bozdu mu? MLX'te ölçtüğümüz model ile llama-server'daki model aynı mı?
2. **Karar:** Tam sistem (şema/gramer + kapı + politika v1.1, kısa istem) golden'da karar kuralını geçiyor mu?
   Golden, Adım 7'de yazılan şablonlardan bağımsızdır (dondurulmuş test şablonları).

## Akış
```
make export-ft                          adaptör + taban → f32 birleştirme → GGUF F32 → Q4_K_M ve Q8_0
make sunucu-ft Q=Q8_0   (2. terminal)   → make gguf-parite Q=Q8_0          dönüşüm doğru mu? (nicemleme etkisi ~0)
make sunucu-ft Q=Q4_K_M (2. terminal)   → make gguf-parite Q=Q4_K_M        4-bit ne kadar bozuyor?
                                         → make gguf-parite-sema Q=Q4_K_M   gramer tür seçimini değiştiriyor mu?
                                         → make eval-ft                     golden · doğrulama · adversarial · OLTA · UCI
make rapor                              docs/eval-report.md
```

## Kararlar
| Karar | Gerekçe |
|---|---|
| Birleştirme **float32** (`merge --dtype float32`) | LoRA farkı küçük (|Δ| ~1e-4); bf16'nın ~3 anlamlı hanesine geri yuvarlamak farkın bir kısmını siler, ardından Q4 ikinci kez yuvarlar. f32 → tek yuvarlama. Script, bf16'da kaybolacak payı ayrıca raporlar (kanıt). |
| **Q8_0 tanı modeli** | Q4 paritesi bozuksa sebebi ayırır: Q8 de bozuksa dönüşüm/şablon hatası, yalnızca Q4 bozuksa nicemleme. |
| Parite **gramersiz** (MLX ölçümüyle aynı koşul), ayrıca **şemalı** | Önce elmayla elma; sonra çalışma anındaki gramerin etkisi ayrı satır. |
| Eval: `--istem kisa` | Eğitimle aynı istem (Adım 7, sablon_parite). Tam istemle ölçmek dağılım dışı olur. |
| UCI yalnızca yerel | Gerçek kişisel e-postalar; model yerel llama-server, dışarı çıkmaz (kod zaten engelliyor). |

## Tahminler (çalıştırmadan önce)
| # | Tahmin |
|---|---|
| G1 | bf16 yuvarlama, Δ'nın göreli olarak ~%10–40'ını bozardı (script ölçecek) |
| G2 | Parite Q8_0: tür uyumu ≥ %98. Q4_K_M: ≥ %93 (eşik %95 sınırda) |
| G3 | Şemalı ölçüm tür doğruluğunu ±0.02'den fazla değiştirmez |
| G4 | Golden (tam sistem): tür makro-F1 0.55–0.70 · dolandırıcılık recall ≥ 0.95 · meşru FPR 0.20–0.50 → **karar kuralı FPR'de geçmez** |
| G5 | Adversarial sızıntı ≤ 2 (politika v1.1 güvenlik ağı) · OLTA ikili recall ≥ 0.70 |
| G6 | Mac'te ~1,5–2 sn/mesaj (çıktı ~80 token) |

## Sonuçlar

### Dönüşüm
- 186 LoRA modülü birleştirildi (scale 10, rank 16). |Δ| ortalama ~9e-4.
- **G1 ❌:** bf16'ya yuvarlansaydı Δ'nın göreli hatası medyan **0.02**, en çok 0.05 olurdu (tahmin 0.10–0.40).
  Fark sanılandan büyük (~1e-3) → bu modelde f32 tedbiri neredeyse gereksizdi; zararsız ve artık ölçülmüş.
- Dönüştürücü uyarıları (`Transformers qwen3_5'i tanımıyor` → config.json'dan okur; `Unknown RoPE type: default`)
  spike'taki ile aynı; parite sistematik bir bozulma göstermedi (aşağıda).
- Q4_K_M 522 MB · Q8_0 795 MB (sha256 → .spike/versions.lock).

### Parite (doğrulama 198, gramersiz, açgözlü; MLX ft-0.8b-v2-it600 ile örnek örnek)
| | tür uyumu | tür doğruluğu (MLX 0.616) | JSON | alıntı | sn/mesaj (Mac) |
|---|---|---|---|---|---|
| Q8_0 | 194/198 = 0.980 | 0.611 (−0.005) | 1.000 | 0.965 | 0.95 |
| Q4_K_M | 167/198 = 0.843 | 0.525 (**−0.091**) | 1.000 | 0.984 | 0.74 |
| Q4_K_M + şema | 168/198 = 0.848 | 0.525 (−0.091) | 1.000 | 0.984 | 0.80 |

- **Q8_0:** önceden konan 0.98 eşiğinin **bir örnek altında** (194; 195 gerekiyordu). Eşik sonradan gevşetilmedi.
  Farklar 4 farklı şablonda birer örnek, yön rastgele → dönüşüm hatası yok; MLX bf16 ↔ llama.cpp Q8 sayısal farkının
  sınır vakaları. **G2 ◐** (Q8 kıl payı ❌, Q4 açıkça ❌).
- **Q4_K_M gerçekten bozuyor:** −0.091 tür doğruluğu, değişimler şablon bazında topaklı (kargo_05 ×4, yatirim ×6,
  odul_05 ×3) ve `kurum_14` (dolandırıcılık) 3 örnekte daha **mesru_islem**'e kaydı → güvenlik yönünde kötüleşme.
  Yorum: 0.8B küçük bir model ve fine-tune'un tür kararları dar marjlı (doğrulamadaki "hep ya da hiç"); 4-bit
  gürültüsü bu marjları çeviriyor.
- **G3 ✅:** şema (gramer) tür seçimini değiştirmedi (167 → 168 uyum, doğruluk aynı).
- **G6 ✅:** Mac'te 0,74–0,95 sn/mesaj (tahmin 1,5–2).

**Karar: dağıtım ve tam ölçüm Q8_0 ile.** VPS'te 6 GB bellek var; 795 MB sorun değil. Bedeli hız: CPU'da üretim
bellek bant genişliğiyle sınırlı, Q8 Q4'ten ~1,3–1,6× yavaş beklenir → VPS p95 ≤ 15 sn kuralı Adım 11'de
(gerekirse Adım 8 sonunda) Q8_0 ile yeniden ölçülecek. Ara seçenek Q6_K/Q5_K_M ancak Q8 VPS'te yetmezse denenir.

### Tam sistem (Q8_0, kısa istem, şema + kapı + politika v1.1)
| set | n | makro-F1 | dol. recall | meşru FPR | kanıt (kapı öncesi) | eşleşme F1 | p95 ms (Mac) |
|---|---|---|---|---|---|---|---|
| golden | 297 | 0.507 | **1.000** ✅ | **0.296** ❌ | 0.970 ✅ | 0.793 | 1.339 |
| doğrulama | 198 | 0.594 | 1.000 | 0.528 | 0.965 | 0.745 | 1.460 |
| adversarial | 30 | – | – | – | 0.956 | – | sızıntı **0** ✅ |
| OLTA (e-posta) | 300 | – | 0.956 | 0.924 | – | – | 1.744 |
| UCI (e-posta) | 300 | – | 1.000 | 0.994 | – | – | 2.274 |

Aynı cetvelde (golden): kural 0.887 / recall 0.975 / FPR 0.000 · gpt-5.4-mini 0.905 / FPR 0.000 · zs-2b 0.236 / FPR 0.43.

**Karne:** G4 ✅ (recall ≥ 0.95, FPR 0.20–0.50 aralığında: 0.296 → karar kuralı FPR'de geçmiyor) ·
G5 ✅ sızıntı 0, OLTA recall 0.956 ≥ 0.70 — ama OLTA/UCI'de FPR ~%92–99: model e-postaların neredeyse tamamına
alarm veriyor (alan dışı; uzun metin, İngilizce UCI). Bu "yüksek recall" bir ayırt etme değil: ayırt etme = recall − FPR
≈ 0.03 (OLTA), ≈ 0.01 (UCI).

**Okuma:** ince ayarlı 0.8B biçimi (JSON, birebir alıntı, kısa çıktı) ve güvenlik ağını (sızıntı 0) öğrendi; ama
"meşru"yu tanımayı öğrenmedi. Dolandırıcılık tarafına yaslanıyor: fail-closed tasarımda bu kaçırmaktan iyidir, ama
FPR 0.30 bir kullanıcıya her üç meşru mesajdan birinde alarm demek. Golden'da kural modeli her ölçüde önde; ancak kural
OLTA'da recall 0.197 → kuralların başarısı şablon diline uyumdan geliyor, gerçek dağılıma taşınmıyor.

## Adım 8b — katmanlı karar: kural birinci, ince ayarlı model ikinci görüş

**Fikir:** iki katmanın kör noktaları farklı. Kural golden'da FPR 0 ama gerçek dağılımda (OLTA) recall 0.197;
ft-0.8b her şeye alarm veriyor ama kapıdan geçen birebir alıntılar üretiyor. Katmanlı: risk önce kural + deterministik
sinyallerle; kural "düşük" derse model ancak **kanıtıyla** riski ORTA'ya çıkarabilir, asla düşüremez.
Model çıktısı (alıntılar, tür) her durumda "Neden?" açıklaması olarak gösterilir.

**Yöntem:** `python -m eval.katmanli`: hiçbir model yeniden çağrılmaz ($0); ft tahminleri sonuç dosyalarından,
kural yerelde; ikisi de aynı politika (v1.1). 6 varyant raporlanır; **★ `ikinci_talep` çalıştırmadan önce seçildi**
(kural düşük + ft dolandırıcılık + kapıdan geçen ≥ 2 kanıt + en az biri ödeme/kod/kimlik TALEBİ → ORTA).
Gerekçe: talep, dolandırıcılığın şablon diline en az bağlı, davranışsal işareti. Golden'a bakıp varyant seçmek
golden'ı ayar setine çevirirdi; diğer varyantlar keşif olarak yazılır, karar ★ ile verilir.

### Tahminler (çalıştırmadan önce)
| # | Tahmin |
|---|---|
| K1 | ★ golden: FPR ≤ 0.03, recall ≥ 0.975 (kuraldan kötü değil) |
| K2 | ★ OLTA: recall kuralın 0.197'sinden ≥ 0.45'e çıkar, FPR ≤ 0.35 → ayırt etme ≥ +0.15 (kural ≈ 0) |
| K3 | `veya` golden FPR ≈ 0.30 (ft'ye eşit): kör birleştirme işe yaramaz, kanıt şartı gerekli |
| K4 | ★ adversarial sızıntı 0 |

### Sonuçlar
| set | kural | ft | veya | ve | ikinci | ★ ikinci_talep |
|---|---|---|---|---|---|---|
| golden F1 / recall / FPR | 0.887 / 0.975 / **0.000** | 0.507 / 1.000 / 0.296 | 0.779 / 1.000 / 0.296 | 0.887 / 0.975 / 0.000 | 0.852 / 1.000 / 0.278 | 0.845 / 0.984 / **0.259** |
| doğrulama F1 / recall / FPR | 0.722 / 0.889 / 0.056 | 0.594 / 1.000 / 0.528 | 0.696 / 1.000 / 0.528 | 0.702 / 0.889 / 0.056 | 0.696 / 1.000 / 0.528 | 0.737 / 0.988 / 0.250 |
| adversarial sızıntı / zor negatif alarm | 0 / 2 | 0 / 6 | 0 / 6 | 0 / 2 | 0 / 6 | 0 / 4 |
| OLTA recall / FPR / ayırt | 0.418 / 0.322 / **+0.096** | 0.956 / 0.924 / +0.032 | 0.973 / 0.924 / +0.049 | 0.401 / 0.322 / +0.079 | 0.956 / 0.915 / +0.041 | 0.615 / 0.644 / **−0.029** |
| UCI recall / FPR / ayırt | 0.492 / 0.372 / +0.120 | 1.000 / 0.994 / +0.006 | 1.000 / 0.994 / +0.006 | 0.492 / 0.372 / +0.120 | 0.958 / 0.939 / +0.019 | 0.817 / 0.622 / +0.195 |

(Kural burada politika v1.1'den geçiyor; Adım 4 tablosundaki kural satırı tür vekiliyle ölçülmüştü: OLTA 0.197/0.195.
Politikanın link güvenlik ağı kurala recall ekliyor ama FPR'yi de aynı oranda artırıyor.)

**Karne:** K1 ❌ (★ golden FPR 0.259, tahmin ≤ 0.03) · K2 ❌ (★ OLTA ayırt −0.029, tahmin ≥ +0.15) · K3 ✅ · K4 ✅.

**Okuma: model kanıt şartıyla bile ayırt edici bilgi eklemiyor.** "Talep" şartı FPR'yi yalnızca 0.296 → 0.259'a
indirdi: model meşru mesajlarda da kapıdan geçen "talep" kanıtı üretiyor (ör. meşru tek kullanımlık kod bildiriminde
"kod" geçen cümleyi `kod_talebi` diye alıntılamak, faturadaki son ödeme cümlesini `odeme_talebi`). Kapı alıntının
mesajda **geçtiğini** doğrular, **anlamının doğru etiketlendiğini** değil (bilinen sınır, ADR-0005'e eklenecek).
OLTA'da ★ kuraldan kötü; UCI'deki +0.195 FPR 0.62 ile kullanılamaz ve UCI zaten İngilizce e-posta.

**İki yan bulgu:**
- **TF-IDF golden 0.491 → 0.689 (FPR 0)**: yalnızca şablon çeşitliliği (Adım 7b) ile. Aynı veriyle ince ayarlı 0.8B
  0.507 / FPR 0.296. Bu veride doğrusal bir model ince ayarlı LLM'yi geçiyor.
- **Kural doğrulamada 0.990 → 0.722**: kurallar eski 11 doğrulama şablonuna göre yazılmıştı; yeni 11 şablonda düştü.
  Kural da şablon diline uyuyor; golden'daki 0.887'nin bir kısmı aynı etki.

**Kök neden adayı: sınıf dengesizliği.** Eğitimde 11 türün 9'u dolandırıcılık: örneklerin yalnızca %18'i meşru/reklam
(272/1496). Model "emin değilsem dolandırıcılık" önselini öğrenmiş: doğrulama ve golden'da hiç dolandırıcılık
kaçırmayıp meşruların üçte birine alarm vermesi bununla tutarlı. Gerçek dünyada oran tam tersi (meşru çoğunlukta).
