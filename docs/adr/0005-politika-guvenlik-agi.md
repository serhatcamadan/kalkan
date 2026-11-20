# ADR-0005: Risk politikası kodda; modelin yanılmasına karşı güvenlik ağı

- **Durum:** Kabul edildi · 2026-11-20

## Bağlam
Adım 4 sonuçları: sentetik golden'daki başarı gerçek dağılıma taşınmıyor (OLTA'da kural modeli ayırt edemiyor,
TF-IDF meşru e-postaların yarısına alarm veriyor). Küçük bir LLM de yanılacak. Yanlış negatifin bedeli (dolandırıcıya
"düşük risk" demek) yanlış pozitiften çok yüksek.

## Karar
1. Model yalnızca **kanıt + tür** üretir. Risk ve öneri metni `kalkan/policy.py` içinde kodla belirlenir.
2. Kırmızı çizgiler (her biri testli, `tests/test_pipeline.py`):
   - Model cevabı yok / zaman aşımı / şema bozuk → **belirsiz** (fail-closed).
   - Enjeksiyon lekesi → en az **orta**. Meşru bir kurum analiz aracına talimat vermez.
   - Model dolandırıcılık dışı dese bile güçlü deterministik işaret (taklit/marka içeren yabancı alan adı, punycode,
     unicode alan adı, gizli karakter, gizlilik ifadesi) → **orta** + "çelişki, resmi kanaldan doğrula".
   - "Düşük" yalnızca: model dolandırıcılık dışı + güçlü işaret yok + leke yok. Metni "işaret bulunamadı".
3. Deterministik sinyaller HAM metinden hesaplanır (Adım 4 adv_12 bulgusu: kanonikleştirme gizli karakteri siliyordu).

## Bedeli
- Güvenlik ağı meşru mesajlarda yanlış alarmı artırabilir (örn. meşru bir kampanyanın kısa linki). Meşru FPR'yi
  model ve politika katmanı için ayrı ayrı raporluyoruz, bu sayede bedel görünür kalıyor.
