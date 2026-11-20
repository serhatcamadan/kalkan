"""KALKAN · Adım 3 · golden test seti için elle inceleme           v1.1 · 2026-11-20

v1.1: --teyit (LLM ön-elemesinden sonra yalnızca işaretlenenler + 20 rastgele "doğru"), insan/LLM birleştirme.
🧪 KESİN DENE (senin işin, ~45–60 dk; ara verip kaldığın yerden devam edebilirsin)

Test setinden tür başına dengeli 150 örnek seçer (tohum sabit) ve tek tek gösterir.
Her örnek için:  [Enter] doğru · t tür yanlış · k kanıt sorunlu · x çıkar (anlamsız/gerçekçi değil) · q kaydet-çık
Kararlar data/golden/inceleme.jsonl dosyasına ANINDA yazılır.

Bitince:  python tools/incele.py --birlestir   → data/golden/golden.jsonl
  (incelenmiş 150'den x'ler çıkar, t düzeltmeleri uygulanır + kalan 147 incelenmemiş test örneği, işaretli)
"""
import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))
from kalkan.schema import Tur  # noqa: E402

KAYIT = KOK / "data/golden/inceleme.jsonl"          # insan kararları (her zaman öncelikli)
LLM = KOK / "data/golden/llm_kararlari.jsonl"        # tools/llm_inceleme.py iceri
ORNEKLEM = 20
N = 150


def secim() -> list[dict]:
    rows = [json.loads(x) for x in open(KOK / "data/splits/test.jsonl", encoding="utf-8")]
    by = defaultdict(list)
    for r in sorted(rows, key=lambda r: r["id"]):   # dosya sırasından bağımsız, kararlı seçim
        by[r["tur"]].append(r)
    rnd = random.Random(150)
    sec = []
    for t in sorted(by):
        rnd.shuffle(by[t])
        sec += by[t][: -(-N // len(by))]   # tavan bölme → tür başına 14
    rnd.shuffle(sec)
    return sec[:N]


def teyit_listesi() -> list[str]:
    llm = {d["id"]: d for d in map(json.loads, open(LLM, encoding="utf-8"))}
    isaretli = [i for i, d in llm.items() if d["karar"] != "dogru"]
    dogru = sorted(i for i, d in llm.items() if d["karar"] == "dogru")
    return isaretli + random.Random(20).sample(dogru, min(ORNEKLEM, len(dogru)))


def incele(sadece: list[str] | None = None) -> None:
    llm = {d["id"]: d for d in map(json.loads, open(LLM, encoding="utf-8"))} if LLM.exists() else {}
    yapilan = {}
    if KAYIT.exists():
        yapilan = {d["id"]: d for d in map(json.loads, open(KAYIT, encoding="utf-8"))}
    KAYIT.parent.mkdir(parents=True, exist_ok=True)
    turler = [t.value for t in Tur]
    sec = secim()
    if sadece is not None:
        sira = {i: n for n, i in enumerate(sadece)}
        sec = sorted((r for r in sec if r["id"] in sira), key=lambda r: sira[r["id"]])
        print(f"Teyit modu: {sum(1 for i in sadece if llm.get(i, {}).get('karar') != 'dogru')} işaretli + "
              f"{min(ORNEKLEM, len(sadece))} rastgele 'doğru' örneklemi. LLM görüşü her örnekte gösterilir.")
    with open(KAYIT, "a", encoding="utf-8") as out:
        for i, r in enumerate(sec, 1):
            if r["id"] in yapilan:
                continue
            print("\n" + "─" * 78)
            print(f"[{i}/{len(sec)}]  {r['id']}  şablon={r['sablon_id']}  gürültü={r['gurultu']}")
            print(f"\nMESAJ (modelin gördüğü):\n  {r['model_girdisi']}\n")
            print(f"ETİKET: {r['tur']}")
            for k in r["hedef"]["kanitlar"]:
                print(f"  • {k['sinyal']:<17} “{k['alinti']}”")
            if r["id"] in llm and sadece is not None:
                d = llm[r["id"]]
                print(f"\n🤖 LLM: {d['karar']}" + (f" → {d.get('yeni_tur')}" if d.get("yeni_tur") else "")
                      + (f" · {d.get('not')}" if d.get("not") else ""))
            c = input("\n[Enter]=doğru  t=tür yanlış  k=kanıt sorunlu  x=çıkar  q=çık > ").strip().lower()
            if c == "q":
                break
            karar = {"id": r["id"], "karar": {"": "dogru", "t": "tur", "k": "kanit", "x": "cikar"}.get(c, "dogru"),
                     "kaynak": "insan"}
            if c == "t":
                for j, t in enumerate(turler):
                    print(f"  {j:2d} {t}")
                karar["yeni_tur"] = turler[int(input("doğru tür no > "))]
            if c in ("k", "x", "t"):
                karar["not"] = input("kısa not (isteğe bağlı) > ").strip()
            out.write(json.dumps(karar, ensure_ascii=False) + "\n")
            out.flush()
    n = sum(1 for _ in open(KAYIT, encoding="utf-8")) if KAYIT.exists() else 0
    print(f"\nKaydedildi: {n} insan kararı → {KAYIT}")


def birlestir() -> None:
    insan = {d["id"]: d for d in map(json.loads, open(KAYIT, encoding="utf-8"))} if KAYIT.exists() else {}
    llm = {d["id"]: d for d in map(json.loads, open(LLM, encoding="utf-8"))} if LLM.exists() else {}
    kararlar = {**llm, **insan}                      # insan kararı LLM'inkini ezer
    rows = [json.loads(x) for x in open(KOK / "data/splits/test.jsonl", encoding="utf-8")]
    out, sayac = [], defaultdict(int)
    for r in rows:
        d = kararlar.get(r["id"])
        r["incelendi"] = "insan" if r["id"] in insan else ("llm" if r["id"] in llm else None)
        if d:
            sayac[d["karar"]] += 1
            if d["karar"] == "cikar":
                continue
            if d["karar"] == "tur":
                r["tur_orijinal"], r["tur"] = r["tur"], d["yeni_tur"]
                r["hedef"]["tur"] = d["yeni_tur"]
            if d.get("not"):
                r["inceleme_notu"] = d["not"]
        out.append(r)
    with open(KOK / "data/golden/golden.jsonl", "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    ortak = [i for i in insan if i in llm]
    uyum = sum(insan[i]["karar"] == llm[i]["karar"] for i in ortak)
    llm_dogru_insan_hata = [i for i in ortak if llm[i]["karar"] == "dogru" and insan[i]["karar"] != "dogru"]
    print(f"golden.jsonl: {len(out)} örnek · insan {len(insan)} · LLM {len(llm)} · son kararlar: {dict(sayac)}")
    if ortak:
        print(f"insan–LLM uyumu: {uyum}/{len(ortak)} (%{100 * uyum // len(ortak)}) · "
              f"LLM'in 'doğru' deyip insanın düzelttiği: {len(llm_dogru_insan_hata)} {llm_dogru_insan_hata[:5]}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--birlestir", action="store_true")
    ap.add_argument("--teyit", action="store_true", help="LLM ön-elemesinden sonra")
    a = ap.parse_args()
    if a.birlestir:
        birlestir()
    elif a.teyit:
        incele(teyit_listesi())
    else:
        incele()
