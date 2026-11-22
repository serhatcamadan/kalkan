"""KALKAN · katman.py — katmanlı karar: kural birinci, model ikinci görüş (ADR-0006)   v1.1 · 2026-11-22

Tek kaynak: hem ürün (kalkan.service.analiz, katman=True) hem değerlendirme (eval/katmanli.py ★) bu fonksiyonu
çağırır. Golden'da ölçülen karar = VPS'te çalışan karar (tests/test_katman.py tekrar oynatarak doğrular).

Kurallar (★ ikinci_talep, golden GÖRÜLMEDEN seçildi):
  0. (v1.1, Adım 9b) Model metnin tamamını göremediyse (girdi_kirpildi) sonuç DÜŞÜK olamaz → en az BELİRSİZ.
  1. Kural (+ politika v1.1) ORTA/YÜKSEK/BELİRSİZ → o karar kalır. Model riski ASLA düşüremez.
  2. Kural DÜŞÜK ve model cevap veremedi (bağlantı, zaman aşımı, bozuk şema) → BELİRSİZ (fail-closed, ADR-0005):
     ürün "düşük" demek için iki katmanın da onayını ister.
  3. Kural DÜŞÜK, model dolandırıcılık türü + kapıdan geçen ≥ 2 kanıt + en az biri ödeme/kod/kimlik TALEBİ → ORTA.
  4. Aksi halde kuralın DÜŞÜK kararı kalır.
Gösterilen tür: kararı veren katmanınki. Gösterilen kanıt: modelin kapıdan geçen alıntıları varsa onlar
("Neden?" açıklaması), yoksa kuralınkiler.
"""
from __future__ import annotations

from dataclasses import dataclass

from .policy import MESAJ, ONERI, TALEP, Karar
from .schema import DOLANDIRICILIK_DISI, DogrulanmisKanit, Risk, Tur

KATMAN_SURUMU = "1.1"        # ADR-0006 · ikinci_talep + kırpılan girdi düşük alamaz
MIN_KANIT = 2


@dataclass
class KatmanKarari:
    karar: Karar
    tur: Tur | None
    kanitlar: list[DogrulanmisKanit]
    kaynak: str                # "kural" | "model_ikinci_gorus" | "model_yok"


def katmanla(kural: Karar, kural_tur: Tur | None, kural_kanit: list[DogrulanmisKanit],
             model_tur: Tur | None, model_kanit: list[DogrulanmisKanit], model_cevap_verdi: bool,
             girdi_kirpildi: bool = False) -> KatmanKarari:
    k = _katmanla(kural, kural_tur, kural_kanit, model_tur, model_kanit, model_cevap_verdi)
    if girdi_kirpildi and k.karar.risk == Risk.dusuk:
        return KatmanKarari(Karar(Risk.belirsiz, "KIRPILDI_DIKKAT", MESAJ_KIRPILDI, k.karar.gerekce + ["girdi_kirpildi"]),
                            k.tur, k.kanitlar, "kirpildi")
    return k


MESAJ_KIRPILDI = ("Mesaj çok uzun olduğu için tamamı incelenemedi. Dikkatli olun: bağlantıya tıklamayın, kod veya "
                  "ödeme paylaşmayın; emin değilseniz gönderen kurumu resmi kanalından arayın.")


def _katmanla(kural: Karar, kural_tur: Tur | None, kural_kanit: list[DogrulanmisKanit],
              model_tur: Tur | None, model_kanit: list[DogrulanmisKanit], model_cevap_verdi: bool) -> KatmanKarari:
    goster = model_kanit or kural_kanit
    if kural.risk != Risk.dusuk:
        return KatmanKarari(kural, kural_tur, goster, "kural")
    if not model_cevap_verdi or model_tur is None:
        k = Karar(Risk.belirsiz, "BELIRSIZ_DIKKAT", MESAJ["belirsiz"], kural.gerekce + ["kural_dusuk_model_yok"])
        return KatmanKarari(k, kural_tur, kural_kanit, "model_yok")
    talepli = any(x.sinyal.value in TALEP for x in model_kanit)
    if model_tur not in DOLANDIRICILIK_DISI and len(model_kanit) >= MIN_KANIT and talepli:
        k = Karar(Risk.orta, f"{model_tur.value.upper()}_IKINCI_GORUS", f"{MESAJ['orta']} {ONERI[model_tur.value]}",
                  kural.gerekce + ["kural_dusuk_model_talepli_kanit"])
        return KatmanKarari(k, model_tur, model_kanit, "model_ikinci_gorus")
    return KatmanKarari(kural, kural_tur, kural_kanit, "kural")
