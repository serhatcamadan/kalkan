"""KALKAN · eval/katmanli.py — kural + ince ayarlı model, KATMANLI karar (çevrimdışı)      v1 · 2026-11-21
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

from kalkan.gate import kapi
from kalkan.injection import tara
from kalkan.normalize import Metin
from kalkan.pii import maskele
from kalkan.policy import POLITIKA_SURUMU, TALEP, karar_ver
from kalkan.schema import DOLANDIRICILIK_DISI, Kanit, Tur
from kalkan.service import GIRDI_MAKS
from kalkan.signals import cikar, maske_araliklari

from .metrics import Tahmin, degerlendir
from .modeller.kural import KuralModeli
from .run_eval import KOK
from .yeniden_puanla import satirlar

SETLER = ["golden", "dogrulama", "adversarial", "olta", "uci"]
SIRA = {"dusuk": 0, "orta": 1, "belirsiz": 1, "yuksek": 2}
VARYANTLAR = ["kural", "ft", "veya", "ve", "ikinci", "ikinci_talep"]
SECILEN = "ikinci_talep"


def karar(o: dict, t: dict) -> tuple[str, str | None, list]:
    """(risk, tür, kapıdan geçen kanıtlar) — yeniden_puanla.puanla ile aynı hat."""
    m = Metin(o["metin"][:GIRDI_MAKS])
    sinyaller = cikar(m)
    maskeli = maskele(m.kanonik, maske_araliklari(sinyaller)).metin
    tur = Tur(t["tur"]) if t.get("tur") and t.get("json_gecerli", True) else None
    kanitlar = []
    for k in t.get("kanitlar", []) if tur else []:
        try:
            kanitlar.append(Kanit.model_validate(k))
        except Exception:  # noqa: BLE001
            pass
    gecen, _ = kapi(kanitlar, maskeli)
    return karar_ver(tur, gecen, sinyaller, tara(maskeli)).risk.value, (tur.value if tur else None), gecen


def birlestir(v: str, k: tuple, f: tuple) -> tuple[str, str | None]:
    (kr, kt, _), (fr, ft, fk) = k, f
    if v == "kural":
        return kr, kt
    if v == "ft":
        return fr, ft
    if v == "veya":
        return (fr, ft) if SIRA[fr] > SIRA[kr] else (kr, kt)
    if v == "ve":
        return (fr, ft) if SIRA[fr] < SIRA[kr] else (kr, kt)
    ft_dol = ft is not None and Tur(ft) not in DOLANDIRICILIK_DISI
    yukselt = kr == "dusuk" and ft_dol and len(fk) >= 2
    if v == "ikinci_talep":
        yukselt = yukselt and any(x.sinyal.value in TALEP for x in fk)
    return ("orta", ft) if yukselt else (kr, kt)


def ozet(set_adi: str, m: dict) -> str:
    if set_adi in ("olta", "uci"):
        r, f = m["dolandiricilik_recall"], m["mesru_fpr"]
        return f"recall {r:.3f} · FPR {f:.3f} · ayırt {r - f:+.3f}"
    if set_adi == "adversarial":
        return f"sızıntı {m['dusuk_risk_sizintisi']} · zor negatif yanlış alarm {m['zor_negatif_yanlis_alarm']}"
    return f"F1 {m['makro_f1']:.3f} · recall {m['dolandiricilik_recall']:.3f} · FPR {m['mesru_fpr']:.3f}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ft", default="ft-0.8b-v2-Q8_0")
    a = ap.parse_args()
    kural = KuralModeli()
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
        sira, kk, ff = [], [], []
        for t in r["tahminler"]:
            o = rows[t["id"]]
            kt = kural.tahmin(o).sozluk()
            kk.append(karar(o, kt))
            ff.append(karar(o, t))
            sira.append(o)
        print(f"{set_adi} (n={len(sira)})")
        for v in VARYANTLAR:
            tah = []
            for k, f, t in zip(kk, ff, r["tahminler"]):
                risk, tur = birlestir(v, k, f)
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
