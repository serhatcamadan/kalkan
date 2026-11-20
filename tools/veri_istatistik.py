"""KALKAN · Adım 3 · veri istatistikleri ve sızıntı denetimi          v1 · 2026-11-20
🧪 KESİN DENE:  python tools/veri_istatistik.py   → ekrana tablo + data/splits/istatistik.json
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))
from kalkan.normalize import Metin  # noqa: E402
from kalkan.schema import DOLANDIRICILIK_DISI, ModelCiktisi, Tur  # noqa: E402
from kalkan.signals import cikar  # noqa: E402

GUCLU = {"link", "kisa_link", "iban", "tutar", "telefon", "marka_iceren_yabanci", "benzer_alan_adi", "supheli_tld",
         "gizlilik_ifadesi", "punycode", "unicode_alan_adi", "gizli_karakter"}
SPLITS = ["egitim", "dogrulama", "test"]


def oku(ad: str) -> list[dict]:
    return [json.loads(x) for x in open(KOK / f"data/splits/{ad}.jsonl", encoding="utf-8")]


def ngramlar(t: str, n: int = 8) -> set:
    w = re.findall(r"\w+", Metin(t).ascii)
    return {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}


def main() -> None:
    veri = {s: oku(s) for s in SPLITS}
    rapor: dict = {}
    print("| bölüm | örnek | şablon | marka | ort. karakter (girdi) | ort. hedef JSON | kanıt/örnek | ascii % | yazım % |")
    print("|---|---|---|---|---|---|---|---|---|")
    for s, rows in veri.items():
        hedef_uz = [len(ModelCiktisi.model_validate(r["hedef"]).kompakt_json()) for r in rows]
        g = Counter(x for r in rows for x in r["gurultu"])
        satir = {
            "ornek": len(rows), "sablon": len({r["sablon_id"] for r in rows}), "marka": len({r["marka"] for r in rows}),
            "ort_girdi": round(sum(len(r["model_girdisi"]) for r in rows) / len(rows)),
            "ort_hedef": round(sum(hedef_uz) / len(rows)),
            "kanit": round(sum(len(r["hedef"]["kanitlar"]) for r in rows) / len(rows), 2),
            "ascii": round(100 * g["ascii"] / len(rows)), "yazim": round(100 * g["yazim"] / len(rows)),
        }
        rapor[s] = satir
        print(f"| {s} | {satir['ornek']} | {satir['sablon']} | {satir['marka']} | {satir['ort_girdi']} | "
              f"{satir['ort_hedef']} | {satir['kanit']} | {satir['ascii']} | {satir['yazim']} |")

    print("\nTür dağılımı:", dict(Counter(r["tur"] for r in veri["egitim"])))
    print("Kanıt sinyal dağılımı (eğitim):", dict(Counter(k["sinyal"] for r in veri["egitim"] for k in r["hedef"]["kanitlar"]).most_common()))

    # ── sızıntı
    sab = {s: {r["sablon_id"] for r in veri[s]} for s in SPLITS}
    mar = {s: {r["marka"] for r in veri[s]} for s in SPLITS}
    txt = {s: {r["metin"] for r in veri[s]} for s in SPLITS}
    egitim_ng = set().union(*(ngramlar(r["metin"]) for r in veri["egitim"]))
    sizinti = {}
    for s in ("dogrulama", "test"):
        ng = [ngramlar(r["metin"]) for r in veri[s]]
        toplam = sum(len(x) for x in ng)
        ortak = sum(len(x & egitim_ng) for x in ng)
        sizinti[s] = {"ortak_sablon": len(sab[s] & sab["egitim"]), "ortak_marka": len(mar[s] & mar["egitim"]),
                      "ayni_metin": len(txt[s] & txt["egitim"]), "8gram_ortak_pct": round(100 * ortak / max(toplam, 1), 1)}
    rapor["sizinti"] = sizinti
    print("\nSızıntı (eğitime karşı):", json.dumps(sizinti, ensure_ascii=False))

    # ── deterministik sinyal kapsaması
    kapsam = defaultdict(lambda: [0, 0])
    mesru_isaret = Counter()
    for r in veri["test"] + veri["dogrulama"] + veri["egitim"]:
        tipler = {x.tip for x in cikar(Metin(r["metin"]))}
        grup = "dolandiricilik_disi" if Tur(r["tur"]) in DOLANDIRICILIK_DISI else "dolandiricilik"
        kapsam[grup][0] += bool(tipler & GUCLU)
        kapsam[grup][1] += 1
        if r["tur"] == "mesru_islem":
            for t in tipler:
                mesru_isaret[t] += 1
    rapor["sinyal_kapsami"] = {g: round(100 * a / b, 1) for g, (a, b) in kapsam.items()}
    print("En az bir güçlü deterministik sinyal %:", rapor["sinyal_kapsami"])
    print("Meşru işlemlerde görülen sinyaller:", dict(mesru_isaret))

    adv = [json.loads(x) for x in open(KOK / "data/adversarial/adversarial.jsonl", encoding="utf-8")]
    rapor["adversarial"] = dict(Counter(a["saldiri"] for a in adv))
    print("Adversarial:", rapor["adversarial"])
    (KOK / "data/splits/istatistik.json").write_text(json.dumps(rapor, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
