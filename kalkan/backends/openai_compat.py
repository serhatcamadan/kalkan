"""KALKAN · backends/openai_compat.py — tek arka uç (ADR-0002)        v1.2 · 2026-11-20

v1.1: max_tokens 200→384, finish_reason kaydı (kesilen cevap ayrı sayılır).
v1.2: BYOK/OpenAI dalı: max_completion_tokens, reasoning_effort, sıcaklık/tohum yok (akıl yürütme modelleri
      reddediyor); önbellekten gelen girdi token'ı ayrıca sayılır (maliyet).

Hem yerel llama-server hem BYOK (OpenAI uyumlu sağlayıcı) aynı istemciyle konuşur. Yalnızca stdlib.
  • API anahtarı nesnede tutulur, ASLA loglanmaz ve repr'de görünmez (BYOK log testi: Adım 9).
  • JSON şeması response_format ile gönderilir (llama-server gramere çevirir → JSON geçerliliği ~%100).
  • llama-server'a özel alanlar (chat_template_kwargs, cache_prompt) yalnızca yerel modda eklenir.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field


@dataclass
class Cevap:
    metin: str | None
    hata: str | None = None
    sure_ms: float = 0.0
    girdi_token: int = 0
    cikti_token: int = 0
    ham: dict = field(default_factory=dict)
    kesildi: bool = False                 # finish_reason == "length": cevap token sınırına çarptı
    onbellek_token: int = 0               # girdinin önbellekten gelen kısmı (OpenAI: %90 indirimli)


class OpenAIUyumlu:
    def __init__(self, base_url: str, model: str = "yerel", api_key: str | None = None, yerel: bool = True,
                 zaman_asimi: float = 30.0, max_tokens: int = 384, akil: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.model, self.yerel, self.zaman_asimi, self.max_tokens = model, yerel, zaman_asimi, max_tokens
        self.akil = akil                    # reasoning_effort (yalnızca BYOK): none | minimal | low …
        self.__anahtar = api_key            # isim karıştırma: dışarıdan kazara okunmasın

    def __repr__(self) -> str:              # anahtar asla görünmez
        return f"OpenAIUyumlu(base_url={self.base_url!r}, model={self.model!r}, yerel={self.yerel})"

    def sohbet(self, sistem: str, kullanici: str, sema: dict) -> Cevap:
        govde = {"model": self.model,
                 "messages": [{"role": "system", "content": sistem}, {"role": "user", "content": kullanici}],
                 "response_format": {"type": "json_schema",
                                     "json_schema": {"name": "kalkan", "schema": sema, "strict": True}}}
        if self.yerel:
            govde.update({"temperature": 0, "max_tokens": self.max_tokens, "seed": 7, "cache_prompt": True,
                          "chat_template_kwargs": {"enable_thinking": False}})
        else:   # akıl yürütme modelleri: max_completion_tokens akıl yürütme token'larını da kapsar
            govde["max_completion_tokens"] = self.max_tokens + (1500 if self.akil not in (None, "none") else 0)
            if self.akil:
                govde["reasoning_effort"] = self.akil
        basliklar = {"Content-Type": "application/json"}
        if self.__anahtar:
            basliklar["Authorization"] = f"Bearer {self.__anahtar}"
        req = urllib.request.Request(f"{self.base_url}/v1/chat/completions", data=json.dumps(govde).encode(),
                                     headers=basliklar, method="POST")
        t0 = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=self.zaman_asimi) as r:
                d = json.loads(r.read())
        except urllib.error.HTTPError as e:
            return Cevap(None, f"HTTP {e.code}: {e.read()[:200].decode(errors='replace')}", (time.perf_counter() - t0) * 1000)
        except Exception as e:  # noqa: BLE001  (zaman aşımı, bağlantı) → fail-closed üst katmanda
            return Cevap(None, f"{type(e).__name__}: {e}", (time.perf_counter() - t0) * 1000)
        u = d.get("usage", {})
        c = d["choices"][0]
        return Cevap(c["message"].get("content"), None, (time.perf_counter() - t0) * 1000,
                     u.get("prompt_tokens", 0), u.get("completion_tokens", 0), {"timings": d.get("timings")},
                     kesildi=c.get("finish_reason") == "length",
                     onbellek_token=(u.get("prompt_tokens_details") or {}).get("cached_tokens", 0))
