# Adım 5 — Uçtan uca hat + yerel zero-shot (Qwen3.5 0.8B / 2B) · v1 · 2026-11-20

## Hat (kalkan/service.py)
```
ham mesaj (≤ 2.000 karakter)
 1 normalize            kanonik metin + uzunluk koruyan görünümler
 2 deterministik sinyal HAM metinden (gizli karakterler dahil), maskelemeden ÖNCE
 3 maskeleme            [TEL] [IBAN] [TCKN] [KART] [EPOSTA] [OTP]
 4 enjeksiyon           kalıp taraması (leke) + <mesaj> sarmalama, içerideki sınırlayıcılar etkisizleştirilir
 5 model                OpenAI uyumlu tek arka uç (yerel llama-server | BYOK), JSON şeması zorunlu
 6 şema                 ModelCiktisi (≤3 kanıt, alıntı ≤80, 11 tür enum)        bozuk → belirsiz
 7 KAPI                 alıntı maskeli metinde birebir değilse düşer
 8 politika (kod)       tür + geçen kanıt + sinyal + leke → risk + öneri       (model risk üretmez)
 9 SistemCevabi         trace_id, kanıt aralıkları, "güvenli" yasak (ADR-0004)
```
Politikanın kırmızı çizgileri (ADR-0005): model yok/bozuk → belirsiz · enjeksiyon lekesi → en az orta ·
model "meşru" dese bile taklit alan adı / gizli karakter / gizlilik baskısı → orta ("çelişki, doğrula").

## Ölçüm değişikliği
Tam hat modellerinde ikili metrikler ve adversarial sızıntı artık **politikanın riskiyle** ölçülür
(alarm = risk ≠ düşük). Taban çizgilerinde türden türetilen vekil ölçüt kalır. Raporda sütun adları aynı.

## Tahminler (zero-shot koşulmadan önce)
| # | Tahmin |
|---|---|
| Z1 | Golden tür makro-F1: 0.8B 0.35–0.55, 2B 0.50–0.70 → ikisi de kural modelinin (0.887) ALTINDA |
| Z2 | JSON geçerliliği ≥ %99 (gramer kısıtı) |
| Z3 | Kapı öncesi kanıt geçerliliği: 0.8B %55–75, 2B %75–90 (Adım 1: %64 / %89) |
| Z4 | Dolandırıcılık recall ≥ 0.95, ama meşru FPR > 0.05 (küçük model her şeye şüpheli der) |
| Z5 | Adversarial "düşük risk" sızıntısı ≤ 1 (politikanın güvenlik ağı sayesinde) |
| Z6 | OLTA ayırt etme gücü (recall − FPR): 2B > TF-IDF'in 0.21'i (dünya bilgisi); 0.8B ≈ 0.2 |
| Z7 | Mac p95: 0.8B < 1.5 sn, 2B < 2.5 sn |
| Z8 | **H2** bu kez kısmen görünür: meşru↔kurum karışması LLM'lerde ortaya çıkar |

## Sonuçlar (2026-11-20, M4, llama-server b12544, Q4_K_M, istem v1.1)
| | 0.8B | 2B | kural (karş.) | TF-IDF (karş.) |
|---|---|---|---|---|
| golden tür makro-F1 | **0.128** | **0.236** | 0.887 | 0.491 |
| golden dol. recall / meşru FPR | 1.00 / **1.00** | 0.98 / **0.43** | 0.98 / 0.00 | 1.00 / 0.00 |
| kapı öncesi kanıt geçerliliği | 0.48 | 0.77 | 1.00 | — |
| kanıt eşleşme F1 | 0.11 | 0.02 | 0.71 | — |
| ort. çıktı token | 113 | **21** | — | — |
| adversarial sızıntı | 0 | 2 | 1 | 2 |
| OLTA recall / FPR (ayırt etme) | 0.99 / 0.99 (**0.00**) | 0.57 / 0.47 (**0.09**) | 0.20 / 0.19 (0.00) | 0.72 / 0.51 (0.21) |
| Mac p95 (golden) | 1.96 sn | 1.02 sn | ~0 | ~0 |

İlk koşu (istem v1, max_tokens 200) iptal edildi: 0.8B JSON'u girintili yazıp 200 token'a çarpıyordu (~%15 kesilme).
v1.1 ile kesilme 0, JSON geçerliliği %100.

## Tahmin karnesi
| # | Tahmin | Sonuç |
|---|---|---|
| Z1 | makro-F1 0.8B 0.35–0.55, 2B 0.50–0.70, ikisi de kuralın altında | ❌ çok daha kötü (0.13 / 0.24). "Kuralın altında" kısmı ✅ |
| Z2 | JSON ≥ %99 | ✅ %100 (v1.1 sonrası) |
| Z3 | kanıt geçerliliği 0.8B %55–75, 2B %75–90 | ❌ 0.8B %48 · ✅ 2B %77 (ama çok az alıntı, aşağıda) |
| Z4 | recall ≥ 0.95, meşru FPR > 0.05 | ✅ ikisi de, aşırı biçimde (0.8B FPR 1.00) |
| Z5 | adversarial sızıntı ≤ 1 | ✅ 0.8B (her şeye alarm) · ❌ 2B (2) |
| Z6 | OLTA'da 2B, TF-IDF'i geçer (dünya bilgisi) | ❌ 0.09 < 0.21 |
| Z7 | Mac p95 0.8B < 1.5 sn, 2B < 2.5 sn | ❌ 0.8B 1.96 sn (uzun çıktı) · ✅ 2B 1.02 sn |

## Bulgular
1. **Zero-shot küçük model bu görevde işe yaramıyor.** 0.8B her şeye dolandırıcılık diyor; teşhis, meşru mesajlarda
   bunun politikadan değil MODELDEN geldiğini gösterdi (meşru mesajlara `sahte_kargo_gumruk`, `yakin_taklidi` vb.).
   2B daha seçici ama türleri ayıramıyor ve dış sette ayırt etme gücü TF-IDF'in altında. Dünya bilgisi 2B ölçeğinde,
   Türkçe ve talimatla yetmiyor.
2. **"Her şeye alarm" kalitesiz bir modeli iyi gösterebilir.** 0.8B recall ve adversarial ölçütlerini mükemmel geçiyor.
   Karar kuralındaki "meşru FPR ≤ %5" şartı tam bunun için var. Tek metrikle model seçilmez.
3. **Aynı istem, iki zıt hata.** 0.8B "kısa ve tek satır" talimatını büyük ölçüde yok sayıyor (113 token). 2B ise aşırı
   uyuyor (21 token). Bu uzunluk büyük ihtimalle kanıtı hiç yazmamak demek: kanıt eşleşme F1 0.02. Kapı öncesi
   geçerliliğin %77 çıkması bu yüzden yanıltıcı: az ama "güvenli" alıntı. (Doğrulama: örnek başına kanıt sayısı.)
4. **Sonuç → yol haritası:** Bu, fine-tune'un (Adım 7) gerekçesini veriyle kuruyor: küçük model talimatla değil,
   örnekle öğrenmeli. Hedef çıktı biçimi (kompakt, kanıt önce, ≤3 kısa alıntı) eğitim verisinde zaten hazır.
   Adım 6'da gpt-5.4-mini aynı istemle ölçülecek: istemin kendisi mi kötü, yoksa model ölçeği mi yetersiz? Bunu o ayırır.

