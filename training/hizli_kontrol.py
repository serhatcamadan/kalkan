"""KALKAN · Adım 7 · MLX tarafında hızlı kontrol (GGUF'a çevirmeden önce)   v1.1 · 2026-11-21
🧪 .spike/venv-mlx/bin/python training/hizli_kontrol.py --adapter training/adapters/ft-0.8b-v1 [--n 198]

Doğrulama setinde (eğitimde görülmeyen ŞABLONLAR ve markalar), çalışma anıyla AYNI istemle
(apply_chat_template, enable_thinking=False), gramer KISITI OLMADAN, açgözlü (greedy) üretim:
  JSON geçerliliği · tür doğruluğu · alıntıların mesajda birebir geçme oranı · ort. çıktı token
Bu sayılar Adım 8'de GGUF Q4_K_M + llama-server ile karşılaştırılacak (MLX ↔ GGUF parite, H4).
--temel ile adaptörsüz (zero-shot) aynı ölçüm → aynı kod yolunda öncesi/sonrası.

v1.1 (Adım 7b):
  • şablon kırılımı (data/sft/valid_meta.jsonl): tür doğruluğu şablon başına; "hep ya da hiç" örüntüsü görünür
  • güvenlik kırılımı (politikadan ÖNCE, yalnızca tür üzerinden):
      kaçan  = dolandırıcılık örneği → mesru_islem / reklam_spam tahmini   (en pahalı hata)
      alarm  = meşru/reklam örneği → dolandırıcılık türü ya da bozuk JSON   (sistem bozuk JSON'da belirsiz = alarm verir)
  • sonuç JSON'u: training/logs/kontrol__<adaptör>.json (mesaj metni YOK; id + tahmin)
"""
import argparse
import json
import time
from collections import Counter, defaultdict
from pathlib import Path

from mlx_lm import generate, load

KOK = Path(__file__).resolve().parents[1]
MESRU = {"mesru_islem", "reklam_spam"}

ap = argparse.ArgumentParser()
ap.add_argument("--adapter", default="training/adapters/ft-0.8b-v1")
ap.add_argument("--temel", action="store_true", help="adaptörsüz (zero-shot) ölç")
ap.add_argument("--n", type=int, default=198)
ap.add_argument("--model", default=".spike/base")
a = ap.parse_args()

model, tok = load(str(KOK / a.model), adapter_path=None if a.temel else str(KOK / a.adapter))
rows = [json.loads(x) for x in open(KOK / "data/sft/valid.jsonl", encoding="utf-8")][: a.n]
meta_yol = KOK / "data/sft/valid_meta.jsonl"
meta = [json.loads(x) for x in open(meta_yol, encoding="utf-8")][: a.n] if meta_yol.exists() else [{}] * len(rows)

gecerli = dogru = alinti_top = alinti_birebir = cikti_tok = 0
kacan = alarm = n_dol = n_mes = 0
karisan, sablon = Counter(), defaultdict(lambda: [0, 0, Counter()])
kayit, t0 = [], time.perf_counter()
for i, (r, m) in enumerate(zip(rows, meta), 1):
    msg = r["messages"]
    istem = tok.apply_chat_template(msg[:-1], tokenize=False, add_generation_prompt=True, enable_thinking=False)
    cikti = generate(model, tok, prompt=istem, max_tokens=256, verbose=False).strip()
    cikti_tok += len(tok.encode(cikti))
    altin = json.loads(msg[-1]["content"])["tur"]
    girdi = msg[1]["content"]
    tahmin = "JSON_BOZUK"
    try:
        d = json.loads(cikti)
        gecerli += 1
        tahmin = d.get("tur")
        for k in d.get("kanitlar", []):
            alinti_top += 1
            alinti_birebir += bool(k.get("alinti")) and k["alinti"] in girdi
    except (ValueError, AttributeError):
        pass
    dogru += tahmin == altin
    if tahmin != altin:
        karisan[(altin, tahmin)] += 1
    if altin in MESRU:
        n_mes += 1
        alarm += tahmin not in MESRU
    else:
        n_dol += 1
        kacan += tahmin in MESRU
    s = sablon[m.get("sablon_id", "?")]
    s[0] += tahmin == altin
    s[1] += 1
    s[2][tahmin] += 1
    kayit.append({"id": m.get("id"), "sablon_id": m.get("sablon_id"), "altin": altin, "tahmin": tahmin})
    if i % 25 == 0:
        print(f"  {i}/{len(rows)}", flush=True)

n = len(rows)
ad = "temel" if a.temel else Path(a.adapter).name
print(f"\n{'TEMEL (zero-shot)' if a.temel else a.adapter} · doğrulama n={n} · {time.perf_counter() - t0:.0f} sn")
print(f"  JSON geçerliliği   {gecerli / n:.3f}   (gramer kısıtı YOK)")
print(f"  tür doğruluğu      {dogru / n:.3f}")
print(f"  alıntı birebir     {alinti_birebir / alinti_top if alinti_top else 0:.3f}  ({alinti_top} alıntı)")
print(f"  ort. çıktı token   {cikti_tok / n:.1f}")
print(f"  KAÇAN dolandırıcılık (→ meşru/reklam)  {kacan}/{n_dol} = {kacan / max(n_dol, 1):.3f}   ← en pahalı hata")
print(f"  YANLIŞ ALARM (meşru/reklam → dol./bozuk) {alarm}/{n_mes} = {alarm / max(n_mes, 1):.3f}")
print(f"  en çok karışan     {karisan.most_common(4)}")
print("  şablon başına (doğru/toplam · en sık tahmin):")
for sid in sorted(sablon):
    d, t, c = sablon[sid]
    isaret = "✅" if d == t else ("❌" if d == 0 else "◐")
    print(f"    {isaret} {sid:13s} {d:2d}/{t:<2d}  {c.most_common(1)[0][0]}")
tam = sum(d == t for d, t, _ in sablon.values())
print(f"  tam bilinen şablon: {tam}/{len(sablon)}")

cikis = KOK / f"training/logs/kontrol__{ad}.json"
cikis.parent.mkdir(parents=True, exist_ok=True)
cikis.write_text(json.dumps({
    "adaptor": ad, "n": n, "json": gecerli / n, "tur": dogru / n,
    "alinti": alinti_birebir / alinti_top if alinti_top else 0, "cikti_token": cikti_tok / n,
    "kacan": kacan, "n_dol": n_dol, "alarm": alarm, "n_mes": n_mes, "tam_sablon": tam, "sablon_sayisi": len(sablon),
    "sablon": {k: {"dogru": v[0], "toplam": v[1], "tahminler": dict(v[2])} for k, v in sorted(sablon.items())},
    "ornekler": kayit}, ensure_ascii=False, indent=1))
print(f"  → {cikis.relative_to(KOK)}")
