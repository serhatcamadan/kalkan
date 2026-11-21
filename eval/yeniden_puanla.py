"""KALKAN · eval/yeniden_puanla.py — politika değişince modeli YENİDEN ÇAĞIRMADAN puanla   v1 · 2026-11-21
🧪 python -m eval.yeniden_puanla      → eval/results/*.json içindeki tam-hat (LLM) sonuçlarını güncel politikayla yeniden puanlar

Neden mümkün? Model yalnızca tür + kanıt üretir; risk KODDA hesaplanır (ADR-0005). Sonuç dosyalarında modelin ham türü
ve kapı öncesi kanıtları saklı. Sinyal, maske, enjeksiyon ve kapı yerel metinden yeniden hesaplanır.
→ Politika değişikliği $0'a, saniyeler içinde tüm modellere uygulanır (gpt-5.4-mini dahil, API çağrısı yok).
Eski risk `risk_onceki` alanında korunur; metrikler yeniden hesaplanır; meta.politika_surumu güncellenir.
"""
from __future__ import annotations

import json
from pathlib import Path

from kalkan.gate import kapi
from kalkan.injection import tara
from kalkan.normalize import Metin
from kalkan.pii import maskele
from kalkan.policy import POLITIKA_SURUMU, karar_ver
from kalkan.schema import Kanit, Tur
from kalkan.service import GIRDI_MAKS
from kalkan.signals import cikar, maske_araliklari

from .metrics import Tahmin, degerlendir
from .run_eval import KOK, SETLER, hazirla_dis, oku, tabakali


def satirlar(meta: dict) -> list[dict]:
    st = meta["set"]
    yol = KOK / SETLER[st]
    if st == "golden" and not yol.exists():
        yol = KOK / "data/splits/test.jsonl"
    rows = oku(yol)
    if st in ("olta", "uci"):
        if meta.get("dis_set_limit"):
            rows = tabakali(rows, meta["dis_set_limit"], "etiket")
        rows = hazirla_dis(rows, st)
    if st == "golden" and meta.get("golden_limit"):
        rows = sorted(tabakali(rows, meta["golden_limit"], "tur"), key=lambda r: r["id"])
    return rows


def puanla(o: dict, t: dict) -> str:
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
    o["model_girdisi"] = maskeli
    return karar_ver(tur, gecen, sinyaller, tara(maskeli)).risk.value


def main() -> None:
    for p in sorted((KOK / "eval/results").glob("*__*.json")):
        r = json.loads(p.read_text(encoding="utf-8"))
        if not any(t.get("risk") for t in r["tahminler"]):
            continue                                   # taban çizgileri: politika yok
        rows = {o["id"]: o for o in satirlar(r["meta"])}
        degisen = 0
        tahminler = []
        for t in r["tahminler"]:
            yeni = puanla(rows[t["id"]], t)
            if yeni != t["risk"]:
                degisen += 1
            t["risk_onceki"] = t.get("risk_onceki", t["risk"])
            t["risk"] = yeni
            tahminler.append(Tahmin(**{k: v for k, v in t.items() if k in Tahmin.__dataclass_fields__}))
        sira = [rows[t["id"]] for t in r["tahminler"]]
        eski = r["metrikler"]
        yeni_m = degerlendir(r["meta"]["set"], sira, tahminler)
        for k in ("gurultuye_gore", "uyarlamalar", "hata_sayisi", "ornek_hata", "kesilen_cevap", "ort_cikti_token", "toplam_usd"):
            if k in eski:
                yeni_m[k] = eski[k]
        r["metrikler"], r["meta"]["politika_surumu"] = yeni_m, POLITIKA_SURUMU
        p.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        oz = {k: (eski.get(k), yeni_m.get(k)) for k in ("dolandiricilik_recall", "mesru_fpr", "dusuk_risk_sizintisi")
              if k in yeni_m}
        print(f"{p.name:40s} değişen risk: {degisen:3d}  (önce, sonra): {oz}")


if __name__ == "__main__":
    main()
