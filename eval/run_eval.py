"""KALKAN · eval/run_eval.py — tek komutla model × veri seti değerlendirmesi v1.1 · 2026-11-20

v1.1: --model llm (tam pipeline, OpenAI uyumlu arka uç) --etiket zs-0.8b --base-url http://127.0.0.1:8080
🧪 KESİN DENE:
  python -m eval.run_eval --model kural tfidf                  # tüm mevcut setler
  python -m eval.run_eval --model tfidf --set golden adversarial
  python -m eval.run_eval --model kural --set olta --limit 2000 # dış sette tabakalı örneklem
  python -m eval.run_eval --model llm --etiket zs-0.8b --set golden adversarial dogrulama
  python -m eval.run_eval --model llm --etiket zs-2b --set olta uci --limit 400

Çıktı: eval/results/<model>__<set>.json  (meta + metrikler + örnek başına tahmin; mesaj METNİ YAZILMAZ)
Sonra: python -m eval.report  → docs/eval-report.md

Kurallar
  • Model ayarı (eşik, C, istem…) yalnızca eğitim + DOĞRULAMA ile yapılır. Golden yalnızca ölçer.
  • Dış setler ham metindir → aynı hat uygulanır: kanonik + PII/OTP maske → model_girdisi.
  • UCI gerçek kişisel e-posta içerir: sonuç dosyasına yalnızca id + tahmin yazılır.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
import time
from pathlib import Path

from kalkan.normalize import Metin
from kalkan.pii import maskele
from kalkan.signals import cikar, maske_araliklari

from .metrics import degerlendir, gruplu_hata
from .modeller.kural import KuralModeli
from .modeller.llm import LLMModeli
from .modeller.tfidf import TfidfModeli

KOK = Path(__file__).resolve().parents[1]
SONUC = KOK / "eval/results"
MODELLER = {"kural": KuralModeli, "tfidf": TfidfModeli, "llm": LLMModeli}
SETLER = {
    "golden": "data/golden/golden.jsonl",
    "dogrulama": "data/splits/dogrulama.jsonl",
    "adversarial": "data/adversarial/adversarial.jsonl",
    "olta": "data/external/olta_tr.jsonl",
    "uci": "data/external/uci_trspam.jsonl",
}


def oku(p: Path) -> list[dict]:
    return [json.loads(x) for x in open(p, encoding="utf-8")]


def hazirla_dis(rows: list[dict], ad: str) -> list[dict]:
    out = []
    for i, r in enumerate(rows):
        m = Metin(r["metin"][:5000])              # çok uzun e-postalar kırpılır (girdi sınırı Adım 9'da 2.000)
        out.append({"id": f"{ad}-{i:05d}", "etiket": r["etiket"], "metin": r["metin"][:5000],   # bellekte kalır, diske yazılmaz
                    "model_girdisi": maskele(m.kanonik, maske_araliklari(cikar(m))).metin})
    return out


def tabakali(rows: list[dict], n: int, anahtar: str, tohum: int = 42) -> list[dict]:
    gruplar: dict = {}
    for r in rows:
        gruplar.setdefault(r[anahtar], []).append(r)
    rnd, out = random.Random(tohum), []
    for k in sorted(gruplar):
        g = gruplar[k]
        out += rnd.sample(g, min(len(g), round(n * len(g) / len(rows))))
    return out


def git_commit() -> str | None:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=KOK, capture_output=True,
                              text=True, timeout=5).stdout.strip() or None
    except Exception:  # noqa: BLE001
        return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", nargs="+", default=["kural", "tfidf"], choices=list(MODELLER))
    ap.add_argument("--set", nargs="+", default=list(SETLER), choices=list(SETLER))
    ap.add_argument("--limit", type=int, help="dış setlerde tabakalı örneklem boyutu")
    ap.add_argument("--etiket", help="llm için sonuç adı (zs-0.8b, zs-2b, gpt-5.4-mini, ft-0.8b …)")
    ap.add_argument("--base-url", default="http://127.0.0.1:8080")
    a = ap.parse_args()

    egitim = oku(KOK / "data/splits/egitim.jsonl")
    dogrulama = oku(KOK / "data/splits/dogrulama.jsonl")
    SONUC.mkdir(parents=True, exist_ok=True)

    for model_adi in a.model:
        if model_adi == "llm":
            if not a.etiket:
                raise SystemExit("--model llm için --etiket gerekli (örn. zs-0.8b)")
            model = LLMModeli(a.etiket, a.base_url)
            model_adi = a.etiket
        else:
            model = MODELLER[model_adi]()
        t0 = time.perf_counter()
        hazirlik = model.hazirla(egitim, dogrulama)
        print(f"▶ {model_adi}: hazırlık {time.perf_counter() - t0:.1f} sn {hazirlik or ''}")
        for set_adi in a.set:
            yol = KOK / SETLER[set_adi]
            if set_adi == "golden" and not yol.exists():
                yol = KOK / "data/splits/test.jsonl"
                print("  ⚠️ golden.jsonl yok → test.jsonl (make golden çalıştır)")
            if not yol.exists():
                print(f"  – {set_adi}: {yol.relative_to(KOK)} yok, atlandı")
                continue
            rows = oku(yol)
            if set_adi in ("olta", "uci"):
                if a.limit:
                    rows = tabakali(rows, a.limit, "etiket")
                rows = hazirla_dis(rows, set_adi)
            t1 = time.perf_counter()
            tahminler = []
            for i, o in enumerate(rows, 1):
                tahminler.append(model.tahmin(o))
                if len(rows) > 50 and i % 50 == 0:
                    print(f"    {set_adi}: {i}/{len(rows)}", end="\r", flush=True)
            if len(rows) > 50:
                print(" " * 40, end="\r")
            met = degerlendir(set_adi, rows, tahminler)
            if hasattr(model, "kesilen"):           # LLM: kesilen cevap ve ortalama çıktı token'ı
                n_t = len(model.cikti_token) or 1
                met["kesilen_cevap"] = model.kesilen
                met["ort_cikti_token"] = round(sum(model.cikti_token) / n_t, 1)
                model.kesilen, model.cikti_token = 0, []
            if set_adi in ("golden", "dogrulama"):
                met["gurultuye_gore"] = gruplu_hata(rows, tahminler, "gurultu")
            sonuc = {
                "meta": {"model": model_adi, "set": set_adi, "n": len(rows), "zaman": time.strftime("%Y-%m-%dT%H:%M:%S"),
                         "git": git_commit(), "veri_sha256": hashlib.sha256(yol.read_bytes()).hexdigest()[:16],
                         "dis_set_limit": a.limit if set_adi in ("olta", "uci") else None, "hazirlik": hazirlik,
                         "sure_sn": round(time.perf_counter() - t1, 2)},
                "metrikler": met,
                "tahminler": [{"id": o["id"], **{k: v for k, v in t.sozluk().items() if k != "ham" or set_adi != "uci"}}
                              for o, t in zip(rows, tahminler)],
            }
            (SONUC / f"{model_adi}__{set_adi}.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=1))
            ozet = {k: met.get(k) for k in ("makro_f1", "dogruluk", "dolandiricilik_recall", "mesru_fpr",
                                            "kapi_oncesi_gecerlilik", "eslesme_f1", "dusuk_risk_sizintisi",
                                            "json_gecerlilik", "p95_ms", "kesilen_cevap", "ort_cikti_token") if k in met}
            print(f"  {set_adi:11s} n={len(rows):5d} {ozet}")


if __name__ == "__main__":
    main()
