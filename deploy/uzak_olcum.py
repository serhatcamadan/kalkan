"""KALKAN · yayındaki sistemin HTTPS üzerinden gecikme ölçümü (Adım 12, Y4)      v1 · 2026-11-23
🧪 Mac'te:  python deploy/uzak_olcum.py https://kalkan-serhat.duckdns.org --n 20

Golden kaynağı olan test bölümünden sabit tohumla n mesaj seçer (sentetik veri; dış setler ASLA gönderilmez),
API'ye HTTPS üzerinden tek tek gönderir. Hız sınırına (dakikada 10) takılmamak için istekler arası ARALIK saniye.
Ölçülen: duvar saati (ağ + TLS + kuyruk + analiz) ve sunucunun bildirdiği sure_ms (yalnızca analiz).
İlk istek ayrıca raporlanır (soğuk önbellek). Mesaj metni çıktıya yazılmaz; yalnızca id ve süreler.
Ayrıca yayındaki kararların golden etiketleriyle tutarlılığı (risk ≠ düşük ⇔ dolandırıcılık) özetlenir.
"""
import argparse
import json
import random
import statistics
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
MESRU = {"mesru_islem", "reklam_spam"}

ap = argparse.ArgumentParser()
ap.add_argument("url")
ap.add_argument("--n", type=int, default=20)
ap.add_argument("--aralik", type=float, default=6.5, help="istekler arası saniye (dakikada ≤ 10 istek)")
ap.add_argument("--tohum", type=int, default=42)
a = ap.parse_args()

rows = [json.loads(x) for x in open(KOK / "data/splits/test.jsonl", encoding="utf-8")]
ornek = random.Random(a.tohum).sample(rows, a.n)
print(f"▶ {a.url} · {a.n} mesaj · aralık {a.aralik} sn · ~{a.n * a.aralik / 60:.1f} dk")

kayit = []
for i, o in enumerate(ornek, 1):
    govde = json.dumps({"mesaj": o["metin"]}).encode()
    istek = urllib.request.Request(f"{a.url.rstrip('/')}/analiz", data=govde,
                                   headers={"Content-Type": "application/json", "User-Agent": "kalkan-uzak-olcum/1"})
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(istek, timeout=90) as y:
            d = json.load(y)
        durum = 200
    except urllib.error.HTTPError as e:
        d, durum = {}, e.code
    duvar = (time.perf_counter() - t0) * 1000
    alarm = d.get("risk") not in (None, "dusuk")
    kayit.append({"id": o["id"], "durum": durum, "duvar_ms": duvar, "sunucu_ms": d.get("sure_ms"),
                  "risk": d.get("risk"), "dogru": (alarm == (o["tur"] not in MESRU)) if durum == 200 else None})
    print(f"  {i:2d}/{a.n} {o['id']:24s} {durum} {duvar:7.0f} ms  sunucu {d.get('sure_ms', '-'):>5} ms  {d.get('risk', '-')}",
          flush=True)
    if i < a.n:
        time.sleep(a.aralik)


def p(x, q):
    x = sorted(x)
    return x[min(len(x) - 1, int(round(q * (len(x) - 1))))]


ok = [k for k in kayit if k["durum"] == 200]
if not ok:
    sys.exit("hiç başarılı istek yok")
sicak = ok[1:] or ok
dv, sv = [k["duvar_ms"] for k in sicak], [k["sunucu_ms"] for k in sicak]
print(f"\nilk istek (soğuk): duvar {ok[0]['duvar_ms']:.0f} ms · sunucu {ok[0]['sunucu_ms']} ms")
print(f"sonraki {len(sicak)}: duvar p50 {statistics.median(dv):.0f} · p95 {p(dv, .95):.0f} · en çok {max(dv):.0f} ms")
print(f"            sunucu p50 {statistics.median(sv):.0f} · p95 {p(sv, .95):.0f} ms   (fark ≈ ağ + TLS)")
print(f"durum kodları: {sorted({k['durum'] for k in kayit})} · alarm kararı golden ile tutarlı: "
      f"{sum(bool(k['dogru']) for k in ok)}/{len(ok)}")
print(f"KARAR: p95 ≤ 15 sn → {'✅' if p(dv, .95) <= 15000 else '❌'}")
cikis = KOK / "deploy/results"
cikis.mkdir(parents=True, exist_ok=True)
yol = cikis / f"uzak-{time.strftime('%Y%m%d-%H%M%S')}.json"
yol.write_text(json.dumps({"url": a.url, "n": a.n, "kayit": kayit}, ensure_ascii=False, indent=1))
print(f"→ {yol.relative_to(KOK)}")
