# Adım 4 — Değerlendirme düzeneği + kural ve TF-IDF taban çizgileri · v1 · 2026-11-20

## Ne kuruldu?
| Dosya | Görev |
|---|---|
| `eval/metrics.py` | Ortak metrikler: tür makro-F1, karışıklık, dolandırıcılık recall / meşru FPR (belirsiz = alarm, fail-closed), kapı öncesi kanıt geçerliliği, kanıt eşleşme F1, JSON geçerliliği, p50/p95, $/1000 |
| `eval/run_eval.py` | Model × set çalıştırıcı. Sonuç dosyasına mesaj METNİ yazılmaz, sürüm izi (git, veri hash) yazılır |
| `eval/report.py` | `docs/eval-report.md` otomatik bölümü + eşik kontrolü (✅/❌) |
| `eval/modeller/kural.py` | Model 0: anahtar kelime + deterministik sinyal kuralları, cümle parçası kanıtı |
| `eval/modeller/tfidf.py` | Model 1: karakter 2–5 + kelime 1–2 gram TF-IDF + lojistik regresyon. C doğrulamada seçilir |

Disiplin: Ayar yalnızca eğitim + doğrulama ile. Golden ve adversarial ölçmek içindir, onlara bakarak düzeltme yapılmaz.
Adversarial'dan çıkan TEK değişiklik bir veri akışı hatasıydı (aşağıda), eşik/kelime ayarı değil.

## Tahminler (golden'ı çalıştırmadan önce yazıldı)
| # | Tahmin | Sonuç |
|---|---|---|
| T1 | Kural golden'da belirgin düşer (0.75–0.90), çünkü doğrulamaya göre ayarlandı | ✅ 0.990 → **0.887** |
| T2 | TF-IDF golden'da doğrulamaya yakın kalır (0.70–0.85) | ❌ 0.716 → **0.491**. Çok daha kötü |
| T3 | TF-IDF dolandırıcılık recall ≥ 0.95 | ✅ 1.000 (meşru FPR 0.000) |
| T4 | En çok karışan çiftler H2'yi doğrular (mesru↔kurum, reklam↔odul) | ❌ Negatifler kusursuz ayrıldı. Karışıklık dolandırıcılık **alt türleri arasında** |

## Bulgular
1. **"Dolandırıcılık mı?" kolay, "hangi tür?" zor.** İki taban çizgisi de golden'da ikili soruda eşikleri geçiyor
   (recall ≥ 0.975, FPR 0). Ama TF-IDF tür sorusunda çöküyor: yatırım ↔ görev (26), ödül ↔ kargo (22), bahis ↔ yatırım (14).
   Şablon bölmesi işe yaradı: TF-IDF eğitim şablonlarının yüzey kelimelerini ezberlemiş, yeni şablonda konuyu tanıyamıyor.
2. **H2 bu modellerde tutmadı.** Zor negatifler (reklam, meşru) sentetik sette fazla "temiz": ret satırı, `[OTP]` maskesi
   gibi güçlü yüzey ipuçları var. Gerçek dünyada bu ayrım zorlaşacak. Dış set (OLTA) ve adversarial zor negatifleri
   (kural 2/7, TF-IDF 3/7 yanlış alarm) bunu şimdiden gösteriyor.
3. **Kural modelinin hatası insan-anlamlı:** "abi oyun içi parayı…" → `yakin_taklidi` (13). "abi" oyuncu jargonunda hitap.
   Bu, LLM'in bağlam avantajını ölçmek için iyi bir test vakası. Golden'a bakarak düzeltilmedi.
4. **Mimari bulgu (adversarial adv_12):** Model kanonik metni görüyor. Kanonikleştirme RLO gibi gizli karakterleri
   siliyor, dolayısıyla `gizli_karakter` sinyali modele hiç ulaşmıyordu. Düzeltme: deterministik sinyaller HAM metinden
   hesaplanıp karara ayrıca verilir. Adım 5 pipeline'ında da böyle olacak (ADR-0003'ün uzantısı).
5. Kural modelinin kanıt alıntıları tasarım gereği %100 birebir. Ama altın kanıtlarla eşleşme F1'i 0.71: doğru yeri
   buluyor, sınırları ve sinyal etiketi kaba. TF-IDF hiç kanıt üretmiyor (**H3 ✅**: tür bulur, nedenini söyleyemez).

## Dış setler (2026-11-20, M4)
| model | OLTA recall | OLTA meşru FPR | ayırt etme (recall − FPR) | UCI spam→alarm | UCI normal→alarm |
|---|---|---|---|---|---|
| kural | 0.197 | 0.195 | **0.002** | 0.395 | 0.321 |
| tfidf | 0.721 | 0.510 | **0.211** | 0.708 | 0.758 |

Tahmin: "ikisi de belirgin düşer, TF-IDF daha çok" → düşüş ✅, sıralama ❌ (TF-IDF recall'u daha yüksek, ama meşru
e-postaların yarısına alarm veriyor).

6. **Sentetik SMS'te öğrenilen hiçbir şey e-postaya taşınmadı.** Kural modelinin recall'u ile FPR'si neredeyse eşit:
   yazı-tura atmaktan farkı yok (recall − FPR ≈ 0). Kurallar SMS'in kalıplarına yazılmış ("24 saat içinde ödeyin"),
   oltalama e-postası başka cümlelerle konuşuyor. TF-IDF ise "uzun ve resmi metin = şüpheli" gibi görünen bir yüzey
   kestirmesi öğrenmiş: UCI'da normal e-postaya spam'den DAHA SIK alarm veriyor (0.76 > 0.71).
7. **Sonuç:** Sentetik golden'daki ✅'ler gerçek dünyayı temsil etmiyor. Model seçiminde dış set sonuçları en az golden
   kadar ağırlık taşımalı. Bu, H1'in ikinci yarısını ("fine-tuned küçük model dış sette daha çok düşer") test etmenin
   zeminini hazırlıyor: fine-tune da aynı sentetik veriden öğrenecek. LLM'lerin dünya bilgisi burada sınanacak.
8. Not: UCI "spam" ≠ dolandırıcılık. Oradaki alarm oranları ikili bir doğru/yanlış değil, "spam'e daha çok mu alarm
   veriyor" sorusunun göstergesi.
