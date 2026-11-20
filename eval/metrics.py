"""KALKAN · eval/metrics.py — tüm modeller için ortak metrikler         v1 · 2026-11-20

Bir modelin her örnek için ürettiği `Tahmin`, altın etiketle karşılaştırılır. Kurallar:
  • tur=None (şema bozuk / zaman aşımı) → fail-closed: "belirsiz". Dolandırıcılık recall'unda YAKALANDI,
    meşru FPR'de ALARM sayılır (kullanıcı "dikkatli ol" görür; düşük risk değildir).
  • Kanıt geçerliliği KAPI ÖNCESİ ölçülür: alıntı model girdisinde birebir geçiyor mu? (Kapı düşürmeden önceki ham kalite.)
  • Kanıt eşleşmesi: aynı sinyal + (biri diğerini içeriyor VEYA kelime Jaccard ≥ 0.5).
"""
from __future__ import annotations

import re
import statistics
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field

from kalkan.normalize import asciile, tr_kucuk
from kalkan.schema import DOLANDIRICILIK_DISI, Tur

DISI = {t.value for t in DOLANDIRICILIK_DISI}
TURLER = [t.value for t in Tur]


@dataclass
class Tahmin:
    tur: str | None                       # None → belirsiz (fail-closed)
    kanitlar: list[dict] = field(default_factory=list)
    json_gecerli: bool = True
    sure_ms: float = 0.0
    maliyet_usd: float = 0.0
    ham: str | None = None                # LLM ham çıktısı (hata ayıklama için)

    def sozluk(self) -> dict:
        return asdict(self)


def dolandiricilik_mi(tur: str | None) -> bool:
    """Fail-closed: belirsiz = alarm."""
    return tur is None or tur not in DISI


def _kelimeler(s: str) -> set[str]:
    return set(re.findall(r"\w+", asciile(tr_kucuk(s))))


def kanit_eslesir(t: dict, g: dict) -> bool:
    if t.get("sinyal") != g.get("sinyal"):
        return False
    a, b = t.get("alinti", ""), g.get("alinti", "")
    if a and b and (a in b or b in a):
        return True
    ka, kb = _kelimeler(a), _kelimeler(b)
    return bool(ka and kb) and len(ka & kb) / len(ka | kb) >= 0.5


def tur_metrikleri(altin: list[str], tahmin: list[str | None]) -> dict:
    n = len(altin)
    dogru = sum(a == t for a, t in zip(altin, tahmin))
    sinif = {}
    for c in TURLER:
        tp = sum(a == c and t == c for a, t in zip(altin, tahmin))
        fp = sum(a != c and t == c for a, t in zip(altin, tahmin))
        fn = sum(a == c and t != c for a, t in zip(altin, tahmin))
        p = tp / (tp + fp) if tp + fp else 0.0
        r = tp / (tp + fn) if tp + fn else 0.0
        f = 2 * p * r / (p + r) if p + r else 0.0
        if tp + fn:                          # yalnızca altında görülen sınıflar makroya girer
            sinif[c] = {"p": round(p, 3), "r": round(r, 3), "f1": round(f, 3), "destek": tp + fn}
    makro = statistics.mean(v["f1"] for v in sinif.values()) if sinif else 0.0
    karisiklik = Counter((a, t or "BELIRSIZ") for a, t in zip(altin, tahmin) if a != t)
    return {"dogruluk": round(dogru / n, 4) if n else 0.0, "makro_f1": round(makro, 4), "sinif": sinif,
            "belirsiz": sum(t is None for t in tahmin),
            "en_cok_karisan": [{"altin": a, "tahmin": t, "n": k} for (a, t), k in karisiklik.most_common(8)],
            "karisiklik_matrisi": {a: dict(Counter(t or "BELIRSIZ" for aa, t in zip(altin, tahmin) if aa == a))
                                   for a in sorted(set(altin))}}


def ikili_metrikler(altin_dol: list[bool], tahmin_dol: list[bool]) -> dict:
    tp = sum(a and t for a, t in zip(altin_dol, tahmin_dol))
    fn = sum(a and not t for a, t in zip(altin_dol, tahmin_dol))
    fp = sum((not a) and t for a, t in zip(altin_dol, tahmin_dol))
    tn = sum((not a) and (not t) for a, t in zip(altin_dol, tahmin_dol))
    return {"dolandiricilik_recall": round(tp / (tp + fn), 4) if tp + fn else None,
            "mesru_fpr": round(fp / (fp + tn), 4) if fp + tn else None,
            "tp": tp, "fn": fn, "fp": fp, "tn": tn}


def kanit_metrikleri(ornekler: list[dict], tahminler: list[Tahmin]) -> dict:
    toplam_alinti = gecerli = 0
    tp = fp = fn = 0
    for o, t in zip(ornekler, tahminler):
        girdi = o["model_girdisi"]
        for k in t.kanitlar:
            toplam_alinti += 1
            gecerli += bool(k.get("alinti")) and k["alinti"] in girdi
        altin = o.get("hedef", {}).get("kanitlar")
        if altin is None:
            continue
        eslenen = set()
        for k in t.kanitlar:
            j = next((i for i, g in enumerate(altin) if i not in eslenen and kanit_eslesir(k, g)), None)
            if j is None:
                fp += 1
            else:
                eslenen.add(j)
                tp += 1
        fn += len(altin) - len(eslenen)
    p = tp / (tp + fp) if tp + fp else None
    r = tp / (tp + fn) if tp + fn else None
    return {"alinti_sayisi": toplam_alinti,
            "kapi_oncesi_gecerlilik": round(gecerli / toplam_alinti, 4) if toplam_alinti else None,
            "eslesme_p": round(p, 4) if p is not None else None,
            "eslesme_r": round(r, 4) if r is not None else None,
            "eslesme_f1": round(2 * p * r / (p + r), 4) if p and r else (0.0 if p is not None else None)}


def sure_maliyet(tahminler: list[Tahmin]) -> dict:
    s = sorted(t.sure_ms for t in tahminler)
    q = lambda x: round(s[min(len(s) - 1, int(x * (len(s) - 1) + 0.5))], 1) if s else None  # noqa: E731
    n = len(tahminler) or 1
    return {"p50_ms": q(.5), "p95_ms": q(.95),
            "json_gecerlilik": round(sum(t.json_gecerli for t in tahminler) / n, 4),
            "usd_1000_mesaj": round(1000 * sum(t.maliyet_usd for t in tahminler) / n, 4)}


def degerlendir(set_adi: str, ornekler: list[dict], tahminler: list[Tahmin]) -> dict:
    """Veri setinin türüne göre uygun metrik paketini döndürür."""
    out: dict = {"n": len(ornekler), **sure_maliyet(tahminler)}
    if set_adi in ("olta", "uci"):
        altin = [o["etiket"] in ("dolandiricilik", "spam") for o in ornekler]
        out.update(ikili_metrikler(altin, [dolandiricilik_mi(t.tur) for t in tahminler]))
        return out
    if set_adi == "adversarial":
        sizinti, yanlis_alarm, tur_kabul = [], [], 0
        for o, t in zip(ornekler, tahminler):
            if o["asla_dusuk"] and not dolandiricilik_mi(t.tur):
                sizinti.append({"id": o["id"], "saldiri": o["saldiri"], "tahmin": t.tur})
            if not o["asla_dusuk"] and dolandiricilik_mi(t.tur):
                yanlis_alarm.append({"id": o["id"], "tahmin": t.tur})
            tur_kabul += t.tur in o["beklenen_turler"]
        out.update({"dusuk_risk_sizintisi": len(sizinti), "sizintilar": sizinti,
                    "zor_negatif_yanlis_alarm": len(yanlis_alarm), "yanlis_alarmlar": yanlis_alarm,
                    "tur_kabul_orani": round(tur_kabul / len(ornekler), 4),
                    "not": "Politika kodu (Adım 5) gelene kadar vekil ölçüt: dolandırıcılık-dışı tür tahmini = düşük risk."})
        out.update(kanit_metrikleri(ornekler, tahminler))
        return out
    altin = [o["tur"] for o in ornekler]
    out.update(tur_metrikleri(altin, [t.tur for t in tahminler]))
    out.update(ikili_metrikler([a not in DISI for a in altin], [dolandiricilik_mi(t.tur) for t in tahminler]))
    out.update(kanit_metrikleri(ornekler, tahminler))
    return out


def gruplu_hata(ornekler: list[dict], tahminler: list[Tahmin], anahtar: str) -> dict:
    """Örn. gürültü tipine göre doğruluk: anahtar='gurultu'."""
    g = defaultdict(lambda: [0, 0])
    for o, t in zip(ornekler, tahminler):
        for k in (o.get(anahtar) or ["(yok)"]):
            g[k][0] += t.tur == o.get("tur")
            g[k][1] += 1
    return {k: {"dogruluk": round(a / b, 3), "n": b} for k, (a, b) in sorted(g.items())}
