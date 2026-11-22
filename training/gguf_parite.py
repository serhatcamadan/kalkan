"""KALKAN · Adım 8 · MLX ↔ GGUF paritesi (H4)                              v1 · 2026-11-21
🧪 llama-server açıkken (make sunucu-ft Q=Q8_0 veya Q4_K_M):
   python training/gguf_parite.py --etiket Q8_0 [--sema] [--n 198]

hizli_kontrol.py ile AYNI doğrulama mesajları, AYNI istem (sistem + <mesaj>), açgözlü, gramersiz (varsayılan)
→ tahminler training/logs/kontrol__<MLX_KAYNAK>.json ile örnek örnek karşılaştırılır:
  • tür uyumu (aynı id'de aynı tür)          hedef ≥ %95 (Q8_0 ≥ %98)
  • tür doğruluğu farkı (GGUF − MLX)         hedef |fark| ≤ 0.03
  • JSON geçerliliği, alıntı birebir
--sema: çalışma anındaki gibi JSON şeması (gramer) ile; tür seçimine etkisini ayrıca görmek için.
Dış ağ yok: yalnızca 127.0.0.1. Mesaj metni çıktı dosyasına YAZILMAZ.
"""
import argparse
import json
import sys
import time
import urllib.request
from collections import Counter
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))
from kalkan.schema import ModelCiktisi  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--etiket", required=True, help="ör. Q8_0, Q4_K_M")
ap.add_argument("--mlx", default="ft-0.8b-v2-it600", help="training/logs/kontrol__<bu>.json")
ap.add_argument("--base-url", default="http://127.0.0.1:8080/v1")
ap.add_argument("--sema", action="store_true")
ap.add_argument("--n", type=int, default=198)
a = ap.parse_args()

mlx = json.loads((KOK / f"training/logs/kontrol__{a.mlx}.json").read_text(encoding="utf-8"))
mlx_tahmin = {o["id"]: o["tahmin"] for o in mlx["ornekler"]}
rows = [json.loads(x) for x in open(KOK / "data/sft/valid.jsonl", encoding="utf-8")][: a.n]
meta = [json.loads(x) for x in open(KOK / "data/sft/valid_meta.jsonl", encoding="utf-8")][: a.n]
sema = ModelCiktisi.llm_json_schema()


def sor(mesajlar):
    govde = {"model": "kalkan", "messages": mesajlar, "temperature": 0, "seed": 42, "max_tokens": 256,
             "cache_prompt": True, "chat_template_kwargs": {"enable_thinking": False}}
    if a.sema:
        govde["response_format"] = {"type": "json_schema", "json_schema": {"name": "kalkan", "schema": sema, "strict": True}}
    istek = urllib.request.Request(f"{a.base_url}/chat/completions", data=json.dumps(govde).encode(),
                                   headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(istek, timeout=120) as y:
        d = json.load(y)
    return d["choices"][0]["message"]["content"].strip(), d.get("usage", {}).get("completion_tokens", 0)


try:
    sor([{"role": "user", "content": "merhaba"}])
except OSError as e:
    sys.exit(f"llama-server'a ulaşılamadı ({a.base_url}): {e}\nAyrı terminalde: make sunucu-ft Q={a.etiket}")

gecerli = dogru = uyum = alinti_top = alinti_ok = tok = 0
mlx_dogru = 0
farklar, kayit, t0 = Counter(), [], time.perf_counter()
for i, (r, m) in enumerate(zip(rows, meta), 1):
    msg = r["messages"]
    cikti, ct = sor(msg[:-1])
    tok += ct
    altin = json.loads(msg[-1]["content"])["tur"]
    tahmin = "JSON_BOZUK"
    try:
        d = json.loads(cikti)
        gecerli += 1
        tahmin = d.get("tur")
        for k in d.get("kanitlar", []):
            alinti_top += 1
            alinti_ok += bool(k.get("alinti")) and k["alinti"] in msg[1]["content"]
    except (ValueError, AttributeError):
        pass
    mt = mlx_tahmin.get(m["id"])
    dogru += tahmin == altin
    mlx_dogru += mt == altin
    uyum += tahmin == mt
    if tahmin != mt:
        farklar[(m["sablon_id"], mt, tahmin)] += 1
    kayit.append({"id": m["id"], "sablon_id": m["sablon_id"], "altin": altin, "gguf": tahmin, "mlx": mt})
    if i % 25 == 0:
        print(f"  {i}/{len(rows)}", flush=True)

n, sure = len(rows), time.perf_counter() - t0
fark = dogru / n - mlx_dogru / n
gecti = uyum / n >= (0.98 if "Q8" in a.etiket.upper() else 0.95) and abs(fark) <= 0.03
print(f"\nGGUF {a.etiket}{' + şema' if a.sema else ''} ↔ MLX {a.mlx} · doğrulama n={n} · {sure:.0f} sn ({sure / n:.2f} sn/mesaj)")
print(f"  tür uyumu (MLX ile aynı)   {uyum}/{n} = {uyum / n:.3f}")
print(f"  tür doğruluğu  GGUF {dogru / n:.3f} · MLX {mlx_dogru / n:.3f} · fark {fark:+.3f}")
print(f"  JSON geçerliliği           {gecerli / n:.3f}")
print(f"  alıntı birebir             {alinti_ok / alinti_top if alinti_top else 0:.3f}  ({alinti_top} alıntı)")
print(f"  ort. çıktı token           {tok / n:.1f}")
if farklar:
    print("  farklı tahminler (şablon, MLX → GGUF):")
    for (sid, mt, gt), c in farklar.most_common(8):
        print(f"    {sid:12s} {mt} → {gt}  ×{c}")
esik = 0.98 if "Q8" in a.etiket.upper() else 0.95
print(f"KARAR: {'✅ PARİTE' if gecti else '❌ PARİTE YOK'}  (uyum eşiği {esik}, |fark| ≤ 0.03)")
cikis = KOK / f"training/logs/parite__{a.etiket}{'_sema' if a.sema else ''}.json"
cikis.write_text(json.dumps({"etiket": a.etiket, "sema": a.sema, "mlx": a.mlx, "n": n, "uyum": uyum / n,
                             "gguf_tur": dogru / n, "mlx_tur": mlx_dogru / n, "json": gecerli / n,
                             "sn_mesaj": sure / n, "ornekler": kayit}, ensure_ascii=False, indent=1))
print(f"  → {cikis.relative_to(KOK)}")
