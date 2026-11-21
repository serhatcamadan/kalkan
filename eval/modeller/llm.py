"""KALKAN · Model 2–4: OpenAI uyumlu LLM, TAM pipeline üzerinden          v1 · 2026-11-20

Zero-shot (yerel llama-server: Qwen3.5 0.8B/2B), sonra gpt-5.4-mini (Adım 6) ve fine-tune (Adım 7–8) aynı sınıfla
ölçülür. Ölçülen şey modelin kendisi değil, ÜRÜN: normalize → sinyal → maske → model → şema → kapı → politika.
  • Tahmin.tur      : modelin ham türü (şema bozuksa None)
  • Tahmin.kanitlar : KAPI ÖNCESİ alıntılar (geçerlilik metriği bunu ölçer)
  • Tahmin.risk     : politikanın son kararı (ikili metrikler ve adversarial sızıntı bunu kullanır)
"""
from __future__ import annotations

import json
import urllib.request

from kalkan.backends.openai_compat import OpenAIUyumlu
from kalkan.service import analiz

from ..metrics import Tahmin


class LLMModeli:
    def __init__(self, ad: str, base_url: str, model: str = "yerel", api_key: str | None = None, yerel: bool = True,
                 fiyat: tuple[float, float, float] = (0.0, 0.0, 0.0), akil: str | None = None,
                 butce_usd: float | None = None):
        self.ad = ad
        self.arka_uc = OpenAIUyumlu(base_url, model=model, api_key=api_key, yerel=yerel, akil=akil)
        self.fiyat = fiyat                         # $/1M: (girdi, önbellekli girdi, çıktı)
        self.butce_usd, self.harcanan = butce_usd, 0.0
        self.ardisik_http_hata = 0
        self.uyusmazlik = 0
        self.kesilen = 0
        self.cikti_token: list[int] = []

    def butce_bitti(self) -> bool:
        return self.butce_usd is not None and self.harcanan >= self.butce_usd

    def hazirla(self, egitim, dogrulama) -> dict:
        bilgi = {"base_url": self.arka_uc.base_url, "model": self.arka_uc.model, "akil": self.arka_uc.akil,
                 "uyarlamalar": self.arka_uc.notlar,
                 "fiyat_usd_1m": self.fiyat, "butce_usd": self.butce_usd}
        if self.arka_uc.yerel:
            try:
                with urllib.request.urlopen(f"{self.arka_uc.base_url}/props", timeout=5) as r:
                    p = json.loads(r.read())
                bilgi["gguf"] = (p.get("model_path") or "").rsplit("/", 1)[-1]
                bilgi["llama_build"] = p.get("build_info")
            except Exception as e:  # noqa: BLE001
                raise SystemExit(f"llama-server'a ulaşılamadı ({self.arka_uc.base_url}): {e}\n"
                                 "Önce ayrı bir terminalde: make sunucu-08  (veya sunucu-2b)")
        return bilgi

    def tahmin(self, o: dict) -> Tahmin:
        sonuc, iz = analiz(o["metin"], self.arka_uc, trace_id=o.get("id"))
        if iz.hata and iz.ham_cikti is None:      # cevap hiç gelmedi: HTTP hatası, bağlantı, zaman aşımı
            self.ardisik_http_hata += 1
            if self.ardisik_http_hata >= 3:      # aynı hatayı yüzlerce kez tekrarlamanın anlamı yok
                raise SystemExit(f"⛔ Arka uç art arda 3 kez cevap vermedi, durduruldu:\n   {iz.hata}\n"
                                 f"   uyarlamalar: {self.arka_uc.notlar or 'yok'}")
        else:
            self.ardisik_http_hata = 0
        if o.get("model_girdisi") not in (None, iz.model_girdisi):
            self.uyusmazlik += 1
        o["model_girdisi"] = iz.model_girdisi          # kanıt geçerliliği modelin GERÇEKTEN gördüğü metne göre
        maliyet = ((iz.girdi_token - iz.onbellek_token) * self.fiyat[0] + iz.onbellek_token * self.fiyat[1]
                   + iz.cikti_token * self.fiyat[2]) / 1e6
        self.harcanan += maliyet
        kanitlar = [{"alinti": k.alinti, "sinyal": getattr(k.sinyal, "value", k.sinyal)} for k in iz.ham_kanitlar]
        self.kesilen += iz.kesildi
        self.cikti_token.append(iz.cikti_token)
        return Tahmin(tur=iz.tur_ham, kanitlar=kanitlar, json_gecerli=iz.json_gecerli, sure_ms=iz.sure_ms,
                      maliyet_usd=maliyet, ham=iz.ham_cikti if not iz.json_gecerli else None, risk=sonuc.risk.value,
                      hata=iz.hata[:300] if iz.hata else None)
