"""KALKAN · Model 0: kural tabanlı sınıflandırıcı (değerlendirme sarmalayıcısı)                     v1.3 · 2026-11-22

v1.3: mantık kalkan/kural.py'ye taşındı (ürün de aynı kodu çalıştırır); bu dosya yalnızca Tahmin'e çevirir.
v1.2: deterministik sinyaller HAM metinden (o["metin"]) alınır. Model girdisi kanonikleştirildiği için RLO gibi
      gizli karakterler orada iz bırakmıyordu (adversarial adv_12 → veri akışı hatası, eşik ayarı değil).
v1.1 (yalnızca DOĞRULAMA hatalarına bakılarak): "ücret" kalıbı "ücretsiz"i yakalıyordu; kazanç vaadi + kanal/link
      tehlike sayılmıyordu; "kod … atar mısın"; reklam ret ifadeleri; ödül konusunda "kredi tanımlandı".

Taban çizgisi. Anahtar kelime sözlükleri taksonomideki ipuçlarından ve alan bilgisinden yazıldı; yalnızca
eğitim + doğrulama setine bakılarak ayarlandı (golden'a göre AYARLANMADI).
Kanıt: eşleşen anahtar kelimenin içinde geçtiği cümle parçası (≤ 80 karakter) → daima mesajda birebir.

Bilinen yanlılık: Şablonları ve bu kuralları aynı kişi (Claude) yazdı. Sentetik sette kurallar olduğundan
iyi görünebilir. Asıl sınav dış set (OLTA-TR) ve adversarial.
"""
from __future__ import annotations

import time

from kalkan.kural import kural_ciktisi
from kalkan.normalize import Metin
from kalkan.signals import cikar

from ..metrics import Tahmin


class KuralModeli:
    ad = "kural"

    def hazirla(self, egitim, dogrulama) -> dict:
        return {}

    def tahmin(self, o: dict) -> Tahmin:
        t0 = time.perf_counter()
        g = o["model_girdisi"]
        tipler = {d.tip for d in cikar(Metin(o["metin"] if o.get("metin") else g))}   # karar: ham metinden
        c = kural_ciktisi(g, tipler)
        return Tahmin(tur=c["tur"], kanitlar=c["kanitlar"], sure_ms=(time.perf_counter() - t0) * 1000)
