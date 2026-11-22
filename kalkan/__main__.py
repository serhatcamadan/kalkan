"""KALKAN · tek mesaj analizi (komut satırı)                           v1.1 · 2026-11-22
Ürün yolu (ADR-0006): kural birinci katman + yerel ince ayarlı model ikinci görüş, kısa istem.
  python -m kalkan "Paketiniz gümrükte, 49,90 TL ödeyin: bit.ly/x"            # yerel llama-server (8080)
  python -m kalkan --base-url http://127.0.0.1:8081 "…"
  python -m kalkan --model-yok "…"     # yalnızca kural: kural orta/yüksek derse o; "düşük" diyemez → belirsiz
  python -m kalkan --yalniz-model "…"  # v1 davranışı (yalnızca model yolu, tam istem), karşılaştırma için
"""
import argparse
import json

from .backends.openai_compat import OpenAIUyumlu
from .service import analiz

ap = argparse.ArgumentParser()
ap.add_argument("mesaj")
ap.add_argument("--base-url", default="http://127.0.0.1:8080")
ap.add_argument("--model-yok", action="store_true")
ap.add_argument("--yalniz-model", action="store_true")
ap.add_argument("--iz", action="store_true", help="ara durumları da göster")
ap.add_argument("--denetim", metavar="YOL", help="metinsiz denetim satırını bu JSONL'e ekle (ör. logs/denetim.jsonl)")
a = ap.parse_args()
arka = None if a.model_yok else OpenAIUyumlu(a.base_url)
if a.yalniz_model:
    sonuc, iz = analiz(a.mesaj, arka)
else:
    sonuc, iz = analiz(a.mesaj, arka, istem="kisa", katman=True)
print(json.dumps(sonuc.model_dump(mode="json"), ensure_ascii=False, indent=1))
if a.denetim:
    from .denetim import Denetci
    Denetci(a.denetim).yaz(a.mesaj, sonuc, iz)
if a.iz:
    print(json.dumps({"model_girdisi": iz.model_girdisi, "ham_cikti": iz.ham_cikti, "hata": iz.hata,
                      "sure_ms": round(iz.sure_ms), "kural": [iz.kural_tur, iz.kural_risk],
                      "model_risk": iz.model_risk, "katman_kaynak": iz.katman_kaynak}, ensure_ascii=False, indent=1))
