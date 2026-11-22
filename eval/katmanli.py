"""KALKAN · eval/katmanli.py — kural + ince ayarlı model, KATMANLI karar (çevrimdışı)      v1.1 · 2026-11-22

v1.1 (Adım 9a): ★ artık kalkan.katman.katmanla ile hesaplanır; hazırlık ve kural katmanı kalkan.service'ten
      (hazirla, kural_karari). Ürünle AYNI kod → tests/test_katman.py servisi tekrar oynatıp eşitliği doğrular.
      Kural katmanı ürün gibi kırpılmış girdinin (GIRDI_MAKS) sinyallerini kullanır; v1 tam metni kullanıyordu
      (yalnızca 2000 karakteri aşan e-postalarda fark eder).
🧪 python -m eval.katmanli [--ft ft-0.8b-v2-Q8_0]

Hiçbir model yeniden çağrılmaz: ft tahminleri eval/results/<ft>__<set>.json'dan okunur, kural modeli yerelde
yeniden çalışır (milisaniye), ikisi de AYNI politika (kalkan.policy, v1.1) ile riske çevrilir; sonra birleştirilir.
Maliyet $0. Mesaj metni hiçbir yere yazılmaz.

Varyantlar (alarm = risk ≠ düşük; belirsiz = alarm):
  kural         yalnızca kural + politika                              (taban)
  ft            yalnızca ince ayarlı model + politika                  (taban)
  veya          ikisinden biri alarm → alarm                            (üst sınır recall, alt sınır FPR)
  ve            ikisi de alarm → alarm                                  (bilgi için)
  ikinci        kural düşük dedi + ft dolandırıcılık dedi + ft'nin kapıdan geçen ≥ 2 kanıtı → ORTA
★ ikinci_talep  ikinci + bu kanıtlardan en az biri TALEP (ödeme / kod / kimlik)  → ORTA      ← ÖNCEDEN SEÇİLEN
Neden önceden seçilen? Golden'a bakarak varyant seçmek golden'ı ayar setine çevirir. ★ çalıştırmadan önce
gerekçeyle seçildi (davranışsal talep, dolandırıcılığın en az şablona bağlı işareti); diğerleri keşif.
★ sonuçları eval/results/katmanli__<set>.json'a yazılır → make rapor onu da tabloya koyar.
Kullanıcıya gösterilen tür: riski veren katmanın türü. Kanıtlar: ft'nin kapıdan geçen alıntıları (açıklama katmanı).
"""
from __future__ import annotations

import argparse
import json

from kalkan.katman import katmanla
from kalkan.policy import POLITIKA_SURUMU, karar_ver
from kalkan.schema import DOLANDIRICILIK_DISI, Tur
from kalkan.service import hazirla, kanitlari_dogrula, kural_karari

from .metrics import Tahmin, degerlendir
from .run_eval import KOK
from .yeniden_puanla import satirlar

SETLER = ["golden", "dogrulama", "adversarial", "kor", "olta", "uci"]
SIRA = {"dusuk": 0, "orta": 1, "belirsiz": 1, "yuksek": 2}
VARYANTLAR = ["kural", "ft", "veya", "ve", "ikinci", "ikinci_talep"]
SECILEN = "ikinci_talep"


def karar(h, t: dict) -> tuple[str, str | None, list, object]:
    """(risk, tür, kapıdan geçen kanıtlar, Karar) — servisle aynı hat."""
    tur = Tur(t["tur"]) if t.get("tur") and t.get("json_gecerli", True) else None
    gecen, _ = kanitlari_dogrula(t.get("kanitlar", []) if tur else [], h.model_girdisi)
    k = karar_ver(tur, gecen, h.sinyaller, h.enjeksiyon)
    return k.risk.value, (tur.value if tur else None), gecen, k


def birlestir(v: str, k: tuple, f: tuple, kirpildi: bool = False) -> tuple[str, str | None]:
    (kr, kt, kk, kkarar), (fr, ft, fk, _) = k, f
    if v == SECILEN:          # ★: ürünle aynı fonksiyon
        kat = katmanla(kkarar, Tur(kt), kk, Tur(ft) if ft else None, fk, model_cevap_verdi=ft is not None,
                       girdi_kirpildi=kirpildi)
        return kat.karar.risk.value, (kat.tur.value if kat.tur else None)
    if v == "kural":
        return kr, kt
    if v == "ft":
        return fr, ft
    if v == "veya":
        return (fr, ft) if SIRA[fr] > SIRA[kr] else (kr, kt)
    if v == "ve":
        return (fr, ft) if SIRA[fr] < SIRA[kr] else (kr, kt)
    ft_dol = ft is not None and Tur(ft) not in DOLANDIRICILIK_DISI
    return ("orta", ft) if (kr == "dusuk" and ft_dol and len(fk) >= 2) else (kr, kt)      # "ikinci"


def ozet(set_adi: str, m: dict) -> str:
    if set_adi in ("olta", "uci"):
        r, f = m["dolandiricilik_recall"], m["mesru_fpr"]
        return f"recall {r:.3f} · FPR {f:.3f} · ayırt {r - f:+.3f}"
    if set_adi in ("adversarial", "kor"):
        return f"sızıntı {m['dusuk_risk_sizintisi']} · zor negatif yanlış alarm {m['zor_negatif_yanlis_alarm']}"
    return f"F1 {m['makro_f1']:.3f} · recall {m['dolandiricilik_recall']:.3f} · FPR {m['mesru_fpr']:.3f}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ft", default="ft-0.8b-v2-Q8_0")
    a = ap.parse_args()
    print(f"katmanlı karar · politika {POLITIKA_SURUMU} · ft={a.ft} · ★ önceden seçilen: {SECILEN}\n")
    for set_adi in SETLER:
        yol = KOK / f"eval/results/{a.ft}__{set_adi}.json"
        if not yol.exists():
            print(f"– {set_adi}: {yol.name} yok, atlandı")
            continue
        r = json.loads(yol.read_text(encoding="utf-8"))
        rows = {o["id"]: o for o in satirlar(r["meta"])}
        eksik = [t["id"] for t in r["tahminler"] if t["id"] not in rows]
        if eksik:   # sonuç dosyası eski veri sürümünden (ör. şablonlar sonradan değişti) → karşılaştırma geçersiz
            print(f"– {set_adi}: {len(eksik)} tahmin güncel veride yok (ör. {eksik[0]}); {a.ft} bu sette yeniden çalıştırılmalı")
            continue
        sira, kk, ff, kirp = [], [], [], []
        for t in r["tahminler"]:
            o = rows[t["id"]]
            h = hazirla(o["metin"])
            kkarar, ktur, kgecen = kural_karari(h)
            kk.append((kkarar.risk.value, ktur.value, kgecen, kkarar))
            ff.append(karar(h, t))
            kirp.append(h.kirpildi)
            sira.append(o)
        print(f"{set_adi} (n={len(sira)})")
        for v in VARYANTLAR:
            tah = []
            for k, f, t, kp in zip(kk, ff, r["tahminler"], kirp):
                risk, tur = birlestir(v, k, f, kp)
                kanit = [x.model_dump(mode="json") for x in f[2]] if v != "kural" else []
                tah.append(Tahmin(tur=tur, kanitlar=kanit, risk=risk, sure_ms=t.get("sure_ms", 0.0)))
            m = degerlendir(set_adi, sira, tah)
            print(f"  {'★' if v == SECILEN else ' '} {v:13s} {ozet(set_adi, m)}")
            if v == SECILEN:
                cikis = {"meta": {**r["meta"], "model": "katmanli", "katmanli": {"ft": a.ft, "varyant": v},
                                  "politika_surumu": POLITIKA_SURUMU},
                         "metrikler": m,
                         "tahminler": [{"id": t["id"], **x.sozluk()} for t, x in zip(r["tahminler"], tah)]}
                (KOK / f"eval/results/katmanli__{set_adi}.json").write_text(
                    json.dumps(cikis, ensure_ascii=False, indent=1), encoding="utf-8")
        print()


if __name__ == "__main__":
    main()
