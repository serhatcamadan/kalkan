"""KALKAN · Adım 7 · SFT verisi (eğitim/doğrulama → MLX sohbet formatı)    v1.1 · 2026-11-21
🧪 python training/build_sft.py   → data/sft/train.jsonl, data/sft/valid.jsonl

Her örnek, ÇALIŞMA ANINDA modele gidenle birebir aynı biçimdedir:
  system    = kisa_sistem_istemi()
  user      = sarmala(model_girdisi)          (maskeli metin, <mesaj> sarmalı)
  assistant = ModelCiktisi.kompakt_json()     (tek satır, ensure_ascii=False: Adım 2'de \\u kaçışı token'ı ~2x yapıyordu)
v1.1: data/sft/valid_meta.jsonl (id, sablon_id, tur; valid.jsonl ile aynı sıra) → hizli_kontrol şablon kırılımı.
Golden ve adversarial ASLA eğitime girmez (yalnızca data/splits/egitim + dogrulama).
"""
import json
import sys
from collections import Counter
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))
from kalkan.injection import sarmala  # noqa: E402
from kalkan.istem import kisa_sistem_istemi  # noqa: E402
from kalkan.schema import ModelCiktisi  # noqa: E402

CIKIS = KOK / "data/sft"


def donustur(r: dict) -> dict:
    hedef = ModelCiktisi.model_validate(r["hedef"]).kompakt_json()
    return {"messages": [{"role": "system", "content": kisa_sistem_istemi()},
                         {"role": "user", "content": sarmala(r["model_girdisi"])},
                         {"role": "assistant", "content": hedef}]}


def main() -> None:
    CIKIS.mkdir(parents=True, exist_ok=True)
    for kaynak, hedef in (("egitim", "train"), ("dogrulama", "valid")):
        rows = [json.loads(x) for x in open(KOK / f"data/splits/{kaynak}.jsonl", encoding="utf-8")]
        with open(CIKIS / f"{hedef}.jsonl", "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(donustur(r), ensure_ascii=False) + "\n")
        if hedef == "valid":   # MLX yalnızca train/valid/test.jsonl okur; meta ayrı dosyada
            with open(CIKIS / "valid_meta.jsonl", "w", encoding="utf-8") as f:
                for r in rows:
                    f.write(json.dumps({k: r[k] for k in ("id", "sablon_id", "tur")}, ensure_ascii=False) + "\n")
        uz = [len(donustur(r)["messages"][2]["content"]) for r in rows]
        print(f"{hedef}.jsonl: {len(rows)} örnek · tür {len(Counter(r['tur'] for r in rows))} · "
              f"hedef ort. {sum(uz) / len(uz):.0f} karakter (en uzun {max(uz)})")
    print(f"sistem istemi: {len(kisa_sistem_istemi())} karakter")


if __name__ == "__main__":
    main()
