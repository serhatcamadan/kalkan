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
(doldurulacak)
