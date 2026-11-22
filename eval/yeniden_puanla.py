"""KALKAN · eval/yeniden_puanla.py — politika değişince modeli YENİDEN ÇAĞIRMADAN puanla   v1.1 · 2026-11-22

v1.1 (Adım 9b hatası): v1 katmanlı sonuçları (sistem-*, katmanli__*) YALNIZCA MODEL politikasıyla yeniden
      puanlıyordu: kararları bozdu (ör. katmanli__uci recall 0.767 → 0.625). Artık:
        • katmanli__*  → atlanır; `make katmanli` yeniden üretir.
        • sistem-* (katman=True) → tahminde `model_tur` varsa servisle AYNI hat (kural + katmanla) ile puanlanır;
          yoksa (eski dosya) v1'in bozduğu risk `risk_onceki`'den geri yüklenir ve "yeniden koşulmalı" denir.
      Hazırlık servisle aynı (`kalkan.service.hazirla`: tam metin sinyalleri, modelin gördüğü kırpılmış girdi).
      Güncel veride olmayan id'li (eski veri sürümü) dosyalar atlanır.
🧪 python -m eval.yeniden_puanla      → eval/results/*.json içindeki tam-hat (LLM) sonuçlarını güncel politikayla yeniden puanlar

Neden mümkün? Model yalnızca tür + kanıt üretir; risk KODDA hesaplanır (ADR-0005). Sonuç dosyalarında modelin ham türü
ve kapı öncesi kanıtları saklı. Sinyal, maske, enjeksiyon ve kapı yerel metinden yeniden hesaplanır.
→ Politika değişikliği $0'a, saniyeler içinde tüm modellere uygulanır (gpt-5.4-mini dahil, API çağrısı yok).
Eski risk `risk_onceki` alanında korunur; metrikler yeniden hesaplanır; meta.politika_surumu güncellenir.
"""
from __future__ import annotations

import json
from pathlib import Path

from kalkan.katman import katmanla
from kalkan.policy import POLITIKA_SURUMU, karar_ver
from kalkan.schema import Tur
from kalkan.service import hazirla, kanitlari_dogrula, kural_karari

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


def puanla(o: dict, t: dict, katman: bool = False) -> str:
    """Servis hattının çevrimdışı eşi. katman=True: t["model_tur"] modelin ham türü, t["kanitlar"] kapı öncesi."""
    h = hazirla(o["metin"])
    tur_alani = t.get("model_tur") if katman else t.get("tur")
    tur = Tur(tur_alani) if tur_alani and t.get("json_gecerli", True) else None
    gecen, _ = kanitlari_dogrula(t.get("kanitlar", []) if tur else [], h.model_girdisi)
    o["model_girdisi"] = h.model_girdisi
    k = karar_ver(tur, gecen, h.sinyaller, h.enjeksiyon)
    if not katman:
        return k.risk.value
    kk, kt, kg = kural_karari(h)
    return katmanla(kk, kt, kg, tur, gecen, model_cevap_verdi=tur is not None, girdi_kirpildi=h.kirpildi).karar.risk.value


def main() -> None:
    for p in sorted((KOK / "eval/results").glob("*__*.json")):
        r = json.loads(p.read_text(encoding="utf-8"))
        if not any(t.get("risk") for t in r["tahminler"]):
            continue                                   # taban çizgileri: politika yok
        if r["meta"].get("model") == "katmanli":
            print(f"{p.name:40s} atlandı: make katmanli yeniden üretir")
            continue
        katman = bool((r["meta"].get("hazirlik") or {}).get("katman"))
        rows = {o["id"]: o for o in satirlar(r["meta"])}
        if any(t["id"] not in rows for t in r["tahminler"]):
            print(f"{p.name:40s} atlandı: eski veri sürümü (id'ler güncel veride yok), yeniden koşulmalı")
            continue
        if katman and not all("model_tur" in t for t in r["tahminler"]):
            if all("risk_onceki" in t for t in r["tahminler"]):      # v1'in bozduğu dosyayı geri al
                for t in r["tahminler"]:
                    t["risk"] = t.pop("risk_onceki")
                tah = [Tahmin(**{k: v for k, v in t.items() if k in Tahmin.__dataclass_fields__}) for t in r["tahminler"]]
                eski = r["metrikler"]
                r["metrikler"] = {**eski, **degerlendir(r["meta"]["set"], [rows[t["id"]] for t in r["tahminler"]], tah)}
                r["meta"]["politika_surumu"] = r["meta"].get("politika_surumu_ilk", "1.1")
                p.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
                print(f"{p.name:40s} GERİ ALINDI (v1 hatası); model_tur yok → güncel politika için yeniden koşulmalı")
            else:
                print(f"{p.name:40s} atlandı: katmanlı sonuçta model_tur yok, yeniden koşulmalı")
            continue
        degisen = 0
        tahminler = []
        for t in r["tahminler"]:
            yeni = puanla(rows[t["id"]], t, katman)
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
