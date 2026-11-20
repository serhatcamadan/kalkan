"""KALKAN · eval/report.py — sonuçlardan eval raporu üretir             v1 · 2026-11-20
🧪 python -m eval.report   → docs/eval-report.md içindeki OTOMATİK bölümü yeniler (elle yazılan kısma dokunmaz)

Karar kuralı (yol haritası): sert kısıtlar → eşikler → eşiği geçen en ucuz model.
Eşikler: dolandırıcılık recall ≥ 0.95 · meşru FPR ≤ 0.05 · kapı öncesi kanıt geçerliliği ≥ 0.95 ·
adversarial'da 0 "düşük risk" sızıntısı · VPS p95 ≤ 15 sn (Adım 8'de ölçülür).
"""
from __future__ import annotations

import json
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
SONUC = KOK / "eval/results"
RAPOR = KOK / "docs/eval-report.md"
BAS, SON = "<!-- OTOMATIK:BAS -->", "<!-- OTOMATIK:SON -->"
ESIK = {"dolandiricilik_recall": (">=", 0.95), "mesru_fpr": ("<=", 0.05), "kapi_oncesi_gecerlilik": (">=", 0.95),
        "dusuk_risk_sizintisi": ("<=", 0)}
MODEL_SIRASI = ["kural", "tfidf", "zs-0.8b", "zs-2b", "gpt-5.4-mini", "ft-0.8b", "ft-2b"]


def _f(x, yuzde=False) -> str:
    if x is None:
        return "—"
    if isinstance(x, float):
        return f"{100 * x:.1f}" if yuzde else f"{x:.3f}"
    return str(x)


def _gecti(ad: str, deger) -> str:
    if ad not in ESIK or deger is None:
        return ""
    op, e = ESIK[ad]
    return " ✅" if (deger >= e if op == ">=" else deger <= e) else " ❌"


def yukle() -> dict:
    out: dict = {}
    for p in sorted(SONUC.glob("*__*.json")):
        r = json.loads(p.read_text(encoding="utf-8"))
        out.setdefault(r["meta"]["model"], {})[r["meta"]["set"]] = r
    return out


def tablo(baslik: list[str], satirlar: list[list[str]]) -> str:
    return "\n".join(["| " + " | ".join(baslik) + " |", "|" + "---|" * len(baslik)]
                     + ["| " + " | ".join(s) + " |" for s in satirlar])


def uret() -> str:
    s = yukle()
    modeller = sorted(s, key=lambda m: (MODEL_SIRASI.index(m) if m in MODEL_SIRASI else 99, m))
    p = ["## Golden test (297 örnek, şablon ve marka ayrık)\n"]
    satir = []
    for m in modeller:
        g = s[m].get("golden", {}).get("metrikler")
        if not g:
            continue
        satir.append([m, _f(g["makro_f1"]), _f(g["dogruluk"]),
                      _f(g["dolandiricilik_recall"]) + _gecti("dolandiricilik_recall", g["dolandiricilik_recall"]),
                      _f(g["mesru_fpr"]) + _gecti("mesru_fpr", g["mesru_fpr"]),
                      _f(g["kapi_oncesi_gecerlilik"]) + _gecti("kapi_oncesi_gecerlilik", g["kapi_oncesi_gecerlilik"]),
                      _f(g["eslesme_f1"]), _f(g["json_gecerlilik"]), _f(g["p50_ms"]), _f(g["p95_ms"]),
                      _f(g["usd_1000_mesaj"])])
    p.append(tablo(["model", "makro-F1 (tür)", "doğruluk", "dol. recall", "meşru FPR", "kanıt geçerlilik (kapı öncesi)",
                    "kanıt eşleşme F1", "JSON geçerlilik", "p50 ms", "p95 ms", "$/1000"], satir))

    p.append("\n\n## Doğrulama (ayar seti) ↔ golden farkı\nBüyük düşüş = doğrulama setine aşırı uyum.\n")
    satir = []
    for m in modeller:
        d, g = s[m].get("dogrulama", {}).get("metrikler"), s[m].get("golden", {}).get("metrikler")
        if d and g:
            satir.append([m, _f(d["makro_f1"]), _f(g["makro_f1"]), f"{g['makro_f1'] - d['makro_f1']:+.3f}"])
    p.append(tablo(["model", "doğrulama makro-F1", "golden makro-F1", "fark"], satir))

    p.append("\n\n## Adversarial (30 örnek)\nVekil ölçüt (politika kodu Adım 5'te): dolandırıcılık dışı tür = düşük risk.\n")
    satir = []
    for m in modeller:
        a = s[m].get("adversarial", {}).get("metrikler")
        if a:
            satir.append([m, _f(a["dusuk_risk_sizintisi"]) + _gecti("dusuk_risk_sizintisi", a["dusuk_risk_sizintisi"]),
                          ", ".join(f"{x['id']} ({x['saldiri']})" for x in a["sizintilar"]) or "—",
                          f"{a['zor_negatif_yanlis_alarm']}/7", _f(a["tur_kabul_orani"])])
    p.append(tablo(["model", "düşük risk sızıntısı", "sızan örnekler", "zor negatif yanlış alarm", "tür kabul"], satir))

    p.append("\n\n## Dış setler (ikili: dolandırıcılık mı?)\nOLTA-TR sentetik oltalama e-postası, UCI gerçek spam/normal e-posta. "
             "İkisi de e-posta; bizim veri SMS. Alan kayması bekleniyor.\n")
    satir = []
    for m in modeller:
        o, u = s[m].get("olta", {}), s[m].get("uci", {})
        if o or u:
            om, um = o.get("metrikler", {}), u.get("metrikler", {})
            satir.append([m, _f(om.get("n")), _f(om.get("dolandiricilik_recall")), _f(om.get("mesru_fpr")),
                          _f(um.get("n")), _f(um.get("dolandiricilik_recall")), _f(um.get("mesru_fpr"))])
    p.append(tablo(["model", "OLTA n", "OLTA recall", "OLTA meşru FPR", "UCI n", "UCI spam→alarm", "UCI normal→alarm"], satir))

    p.append("\n\n## En çok karışan tür çiftleri (golden)\n")
    for m in modeller:
        g = s[m].get("golden", {}).get("metrikler")
        if g:
            p.append(f"- **{m}**: " + ", ".join(f"{x['altin']} → {x['tahmin']} ({x['n']})" for x in g["en_cok_karisan"][:4]))
    p.append("\n\n## Gürültü tipine göre doğruluk (golden)\n")
    gur = sorted({k for m in modeller for k in s[m].get("golden", {}).get("metrikler", {}).get("gurultuye_gore", {})})
    satir = []
    for m in modeller:
        gg = s[m].get("golden", {}).get("metrikler", {}).get("gurultuye_gore")
        if gg:
            satir.append([m] + [_f(gg.get(k, {}).get("dogruluk")) for k in gur])
    p.append(tablo(["model"] + gur, satir))
    meta = [f"`{m}/{st}`: git {r['meta']['git']} · veri {r['meta']['veri_sha256']} · {r['meta']['zaman']}"
            for m in modeller for st, r in s[m].items()]
    p.append("\n\n<details><summary>Sürüm izleri</summary>\n\n" + "\n".join(f"- {x}" for x in meta) + "\n</details>")
    return "\n".join(p)


def main() -> None:
    govde = uret()
    if RAPOR.exists():
        eski = RAPOR.read_text(encoding="utf-8")
        if BAS in eski and SON in eski:
            yeni = eski.split(BAS)[0] + BAS + "\n" + govde + "\n" + SON + eski.split(SON)[1]
            RAPOR.write_text(yeni, encoding="utf-8")
            print(f"güncellendi: {RAPOR}")
            return
    RAPOR.write_text("# Kalkan — değerlendirme raporu\n\nElle yazılan yorumlar bu bölümün DIŞINA yazılır; "
                     f"`python -m eval.report` yalnızca aradaki kısmı yeniler.\n\n{BAS}\n{govde}\n{SON}\n", encoding="utf-8")
    print(f"oluşturuldu: {RAPOR}")


if __name__ == "__main__":
    main()
