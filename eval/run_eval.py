"""KALKAN · eval/run_eval.py — tek komutla model × veri seti değerlendirmesi v1.1 · 2026-11-20

v1.1: --model llm (tam pipeline, OpenAI uyumlu arka uç) --etiket zs-0.8b --base-url http://127.0.0.1:8080
🧪 KESİN DENE:
  python -m eval.run_eval --model kural tfidf                  # tüm mevcut setler
  python -m eval.run_eval --model tfidf --set golden adversarial
  python -m eval.run_eval --model kural --set olta --limit 2000 # dış sette tabakalı örneklem
  python -m eval.run_eval --model llm --etiket zs-0.8b --set golden adversarial dogrulama
  python -m eval.run_eval --model llm --etiket zs-2b --set olta uci --limit 400
  OPENAI_API_KEY=… python -m eval.run_eval --model llm --etiket gpt-5.4-mini --byok --set golden --pilot 20 --butce-usd 0.05

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
import os
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
FIYAT = {"gpt-5.4-mini": (0.75, 0.075, 4.50), "gpt-5.4-nano": (0.20, 0.02, 1.25)}   # $/1M, 2026-11-20 doğrulandı
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
    ap.add_argument("--byok", action="store_true", help="OpenAI API (anahtar OPENAI_API_KEY ortam değişkeninden)")
    ap.add_argument("--api-model", default="gpt-5.4-mini")
    ap.add_argument("--akil", default="none", help="reasoning_effort (BYOK): none|minimal|low|medium")
    ap.add_argument("--butce-usd", type=float, help="bu çalıştırmada harcanabilecek en fazla $ (aşılınca durur)")
    ap.add_argument("--pilot", type=int, help="her setin ilk N örneği (maliyet/süre ölçümü için)")
    ap.add_argument("--istem", default="tam", choices=["tam", "kisa"], help="fine-tune modelleri: kisa")
    ap.add_argument("--katman", action="store_true", help="ürün yolu (ADR-0006): kural + model ikinci görüş")
    ap.add_argument("--golden-limit", type=int, help="golden'dan tür başına eşit, sabit tohumlu alt küme (pahalı modeller)")
    a = ap.parse_args()

    egitim = oku(KOK / "data/splits/egitim.jsonl")
    dogrulama = oku(KOK / "data/splits/dogrulama.jsonl")
    SONUC.mkdir(parents=True, exist_ok=True)

    for model_adi in a.model:
        if model_adi == "llm":
            if not a.etiket:
                raise SystemExit("--model llm için --etiket gerekli (örn. zs-0.8b)")
            if a.byok:
                anahtar = os.environ.get("OPENAI_API_KEY")
                if not anahtar:
                    raise SystemExit("OPENAI_API_KEY ortam değişkeni yok (anahtarı dosyaya YAZMA; terminalde ayarla).")
                model = LLMModeli(a.etiket, os.environ.get("KALKAN_OPENAI_BASE_URL", "https://api.openai.com"), model=a.api_model, api_key=anahtar, yerel=False,
                                  fiyat=FIYAT.get(a.api_model, (0.0, 0.0, 0.0)), akil=a.akil, butce_usd=a.butce_usd,
                                  istem=a.istem)
                del anahtar
            else:
                model = LLMModeli(a.etiket, a.base_url, butce_usd=a.butce_usd, istem=a.istem, katman=a.katman)
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
            if set_adi == "uci" and getattr(model, "arka_uc", None) is not None and not model.arka_uc.yerel:
                print("  – uci: GERÇEK kişisel e-postalar → dış API'ye gönderilmez (yalnızca yerel modeller), atlandı")
                continue
            rows = oku(yol)
            if a.pilot:
                rows = rows[: a.pilot]
            if set_adi == "golden" and a.golden_limit:
                rows = sorted(tabakali(rows, a.golden_limit, "tur"), key=lambda r: r["id"])
            if set_adi in ("olta", "uci"):
                if a.limit:
                    rows = tabakali(rows, a.limit, "etiket")
                rows = hazirla_dis(rows, set_adi)
            t1 = time.perf_counter()
            tahminler = []
            for i, o in enumerate(rows, 1):
                if getattr(model, "butce_bitti", lambda: False)():
                    print(f"  ⛔ bütçe doldu (${model.harcanan:.4f}); {set_adi} {i - 1}/{len(rows)} örnekte kesildi")
                    rows = rows[: i - 1]
                    break
                tahminler.append(model.tahmin(o))
                if len(rows) > 50 and i % 50 == 0:
                    print(f"    {set_adi}: {i}/{len(rows)}", end="\r", flush=True)
            if len(rows) > 50:
                print(" " * 40, end="\r")
            met = degerlendir(set_adi, rows, tahminler)
            if getattr(model, "arka_uc", None) is not None:
                met["uyarlamalar"] = list(model.arka_uc.notlar)
                hatalar = [t.hata for t in tahminler if t.hata]
                met["hata_sayisi"] = len(hatalar)
                if hatalar:
                    met["ornek_hata"] = hatalar[0][:200]
            if not rows:
                continue
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
                         "dis_set_limit": a.limit if set_adi in ("olta", "uci") else None,
                         "golden_limit": a.golden_limit if set_adi == "golden" else None, "hazirlik": hazirlik,
                         "sure_sn": round(time.perf_counter() - t1, 2)},
                "metrikler": {**met, **({"toplam_usd": round(sum(t.maliyet_usd for t in tahminler), 4)}
                                         if any(t.maliyet_usd for t in tahminler) else {})},
                "tahminler": [{"id": o["id"], **{k: v for k, v in t.sozluk().items() if k != "ham" or set_adi != "uci"}}
                              for o, t in zip(rows, tahminler)],
            }
            (SONUC / f"{model_adi}__{set_adi}.json").write_text(json.dumps(sonuc, ensure_ascii=False, indent=1))
            ozet = {k: met.get(k) for k in ("makro_f1", "dogruluk", "dolandiricilik_recall", "mesru_fpr",
                                            "kapi_oncesi_gecerlilik", "eslesme_f1", "dusuk_risk_sizintisi",
                                            "json_gecerlilik", "p95_ms", "kesilen_cevap", "ort_cikti_token",
                                            "hata_sayisi", "uyarlamalar") if k in met}
            print(f"  {set_adi:11s} n={len(rows):5d} {ozet}")
            if hasattr(model, "harcanan") and model.harcanan:
                print(f"    💵 bu set ${sum(t.maliyet_usd for t in tahminler):.4f} · çalıştırma toplamı ${model.harcanan:.4f}")


if __name__ == "__main__":
    main()
