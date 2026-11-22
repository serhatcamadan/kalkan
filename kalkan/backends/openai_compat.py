"""KALKAN · backends/openai_compat.py — tek arka uç (ADR-0002)        v1.4 · 2026-11-22

v1.4 (Adım 9b): hata metinleri anahtardan temizlenir (sağlayıcı gövdesi anahtarı yankılasa bile); anahtar _Gizli
      sarmalayıcıda: vars()/__dict__/str/repr/pickle onu göstermez (test bunu yakaladı: isim karıştırma vars()'a
      karşı koruma sağlamıyordu). Kasıtlı okuma hâlâ mümkün; amaç KAZARA sızıntıyı (hata ayıklama dökümü, log) önlemek.
v1.1: max_tokens 200→384, finish_reason kaydı (kesilen cevap ayrı sayılır).
v1.3: HTTP 400'de tek seferlik uyarlama: şema anahtar kelimesi reddedilirse sadeleştirilmiş şema (maxLength/maxItems/
      minLength/title yok), reasoning_effort reddedilirse parametresiz tekrar. Uyarlama kalıcıdır ve `notlar`a yazılır.
v1.2: BYOK/OpenAI dalı: max_completion_tokens, reasoning_effort, sıcaklık/tohum yok (akıl yürütme modelleri
      reddediyor); önbellekten gelen girdi token'ı ayrıca sayılır (maliyet).

Hem yerel llama-server hem BYOK (OpenAI uyumlu sağlayıcı) aynı istemciyle konuşur. Yalnızca stdlib.
  • API anahtarı nesnede tutulur, ASLA loglanmaz ve repr'de görünmez (BYOK log testi: Adım 9).
  • JSON şeması response_format ile gönderilir (llama-server gramere çevirir → JSON geçerliliği ~%100).
  • llama-server'a özel alanlar (chat_template_kwargs, cache_prompt) yalnızca yerel modda eklenir.
"""
from __future__ import annotations

import json
import re
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


class _Gizli:
    """Değeri yalnızca .deger() ile verir; her türlü dökümde '<gizli>' görünür, serileştirilemez."""
    __slots__ = ("_d",)

    def __init__(self, d: str):
        self._d = d

    def deger(self) -> str:
        return self._d

    def __repr__(self) -> str:
        return "<gizli>"

    __str__ = __repr__

    def __reduce__(self):
        raise TypeError("gizli değer serileştirilemez")


class OpenAIUyumlu:
    def __init__(self, base_url: str, model: str = "yerel", api_key: str | None = None, yerel: bool = True,
                 zaman_asimi: float = 30.0, max_tokens: int = 384, akil: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.model, self.yerel, self.zaman_asimi, self.max_tokens = model, yerel, zaman_asimi, max_tokens
        self.akil = akil                    # reasoning_effort (yalnızca BYOK): none | minimal | low …
        self.sade_sema = False
        self.notlar: list[str] = []
        self.__anahtar = _Gizli(api_key) if api_key else None   # vars()/repr/log'da görünmez

    def __repr__(self) -> str:              # anahtar asla görünmez
        return f"OpenAIUyumlu(base_url={self.base_url!r}, model={self.model!r}, yerel={self.yerel})"

    def _temizle(self, metin: str) -> str:
        """Sağlayıcı hata gövdesini aynen döndürebilir (bazıları isteği/anahtarı yankılar): anahtar ve
        'sk-…' / 'Bearer …' biçimli her şey maskelenir. Hata metni Iz'e, sonuç dosyasına ve ekrana gider."""
        if self.__anahtar:
            metin = metin.replace(self.__anahtar.deger(), "***")
        metin = re.sub(r"Bearer\s+\S+", "Bearer ***", metin)
        return re.sub(r"\bsk-[A-Za-z0-9_\-]{8,}", "sk-***", metin)

    def sohbet(self, sistem: str, kullanici: str, sema: dict) -> Cevap:
        c = self._sohbet(sistem, kullanici, sema)
        if c.hata and c.hata.startswith("HTTP 400") and not self.yerel:
            h = c.hata.lower()
            if "reasoning" in h and self.akil:
                self.notlar.append(f"reasoning_effort={self.akil} reddedildi → parametresiz")
                self.akil = None
                return self._sohbet(sistem, kullanici, sema)
            if ("schema" in h or "json" in h or "invalid" in h) and not self.sade_sema:
                self.notlar.append("şema reddedildi → sadeleştirilmiş şema (sınırları hat uygular)")
                self.sade_sema = True
                return self._sohbet(sistem, kullanici, sema)
        return c

    def _sohbet(self, sistem: str, kullanici: str, sema: dict) -> Cevap:
        if self.sade_sema:
            sema = _sadelestir(sema)
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
            basliklar["Authorization"] = f"Bearer {self.__anahtar.deger()}"
        req = urllib.request.Request(f"{self.base_url}/v1/chat/completions", data=json.dumps(govde).encode(),
                                     headers=basliklar, method="POST")
        t0 = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=self.zaman_asimi) as r:
                d = json.loads(r.read())
        except urllib.error.HTTPError as e:
            govde_hata = e.read()[:400].decode(errors="replace")
            return Cevap(None, self._temizle(f"HTTP {e.code}: {govde_hata}"), (time.perf_counter() - t0) * 1000)
        except Exception as e:  # noqa: BLE001  (zaman aşımı, bağlantı) → fail-closed üst katmanda
            return Cevap(None, self._temizle(f"{type(e).__name__}: {e}"), (time.perf_counter() - t0) * 1000)
        u = d.get("usage", {})
        c = d["choices"][0]
        return Cevap(c["message"].get("content"), None, (time.perf_counter() - t0) * 1000,
                     u.get("prompt_tokens", 0), u.get("completion_tokens", 0), {"timings": d.get("timings")},
                     kesildi=c.get("finish_reason") == "length",
                     onbellek_token=(u.get("prompt_tokens_details") or {}).get("cached_tokens", 0))


_ATILACAK = {"maxLength", "minLength", "maxItems", "minItems", "title", "pattern", "format"}


def _sadelestir(d):
    if isinstance(d, dict):
        return {k: _sadelestir(v) for k, v in d.items() if k not in _ATILACAK}
    if isinstance(d, list):
        return [_sadelestir(v) for v in d]
    return d
