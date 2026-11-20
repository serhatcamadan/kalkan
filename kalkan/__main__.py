"""KALKAN · tek mesaj analizi (komut satırı)                           v1 · 2026-11-20
  python -m kalkan "Paketiniz gümrükte, 49,90 TL ödeyin: bit.ly/x"            # yerel llama-server (8080)
  python -m kalkan --base-url http://127.0.0.1:8081 "…"
  python -m kalkan --model-yok "…"                                           # yalnızca kurallar → belirsiz
"""
import argparse
import json

from .backends.openai_compat import OpenAIUyumlu
from .service import analiz

ap = argparse.ArgumentParser()
ap.add_argument("mesaj")
ap.add_argument("--base-url", default="http://127.0.0.1:8080")
ap.add_argument("--model-yok", action="store_true")
ap.add_argument("--iz", action="store_true", help="ara durumları da göster")
a = ap.parse_args()
sonuc, iz = analiz(a.mesaj, None if a.model_yok else OpenAIUyumlu(a.base_url))
print(json.dumps(sonuc.model_dump(mode="json"), ensure_ascii=False, indent=1))
if a.iz:
    print(json.dumps({"model_girdisi": iz.model_girdisi, "ham_cikti": iz.ham_cikti, "hata": iz.hata,
                      "sure_ms": round(iz.sure_ms)}, ensure_ascii=False, indent=1))
