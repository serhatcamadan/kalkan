"""KALKAN · api.py — HTTP API + demo arayüzü (Adım 10)                   v1.2 · 2026-11-23
🧪 uvicorn kalkan.api:uygulama --factory --host 127.0.0.1 --port 8000   (llama-server: KALKAN_LLAMA_URL, varsayılan :8080)

Uç noktalar
  GET  /            demo arayüzü (kalkan/web/index.html; tek dosya, dış kaynak yok)
  POST /analiz      {"mesaj": "..."} → ürün yolu (ADR-0006: kural + ince ayarlı model, kısa istem)
  GET  /saglik      API ve model sunucusu ayakta mı, sürümler
  HEAD / ve /saglik (v1.2): çalışma süresi izleyicileri çoğunlukla HEAD gönderir (Adım 11'de 405 dönüyordu)

Güvenlik (Adım 9b'nin devamı)
  • Mesaj HİÇBİR yere yazılmaz: denetim kaydı metinsiz (kalkan/denetim.py), erişim logu yalnızca yol ve durum kodu.
  • Girdi sınırı: HAM_MAKS (10.000) karakter → fazlası 413. Boş mesaj → 422.
  • Hız sınırı: IP başına kayan pencere (dakikada / günde). IP yalnızca KALKAN_GUVENILIR_VEKIL=1 iken
    X-Forwarded-For'un SON öğesinden okunur (güvenilir tek vekilin, Caddy'nin, eklediği adres; ilk öğeler istemcinin
    kendi yazabildiği değerler olabilir). Aksi halde bağlantı adresi (başlık taklidi engeli).
  • Eşzamanlılık: llama-server tek yuvalı (-np 1) → en çok 1 model çağrısı; kuyrukta en çok KUYRUK_MAKS bekleyen,
    fazlası hemen 503 "meşgul" (kuyruk sınırsız büyüyüp belleği ve gecikmeyi patlatmasın).
  • Model erişilemezse servis fail-closed çalışır (kural orta/yüksek → o; aksi halde belirsiz), 200 döner.
  • Başlıklar: CSP (yalnızca kendi kaynağı), nosniff, no-referrer, çerçeveleme yasak. CORS yok (aynı köken).
"""
from __future__ import annotations

import os
import threading
import time
from collections import defaultdict, deque
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from . import __version__
from .backends.openai_compat import OpenAIUyumlu
from .denetim import Denetci
from .katman import KATMAN_SURUMU
from .policy import POLITIKA_SURUMU
from .service import HAM_MAKS, analiz, hazirla

WEB = Path(__file__).parent / "web"
TUR_ADI = {
    "sahte_kargo_gumruk": "Sahte kargo / gümrük", "kurum_taklidi": "Kurum taklidi (banka, operatör, e-ticaret, kamu)",
    "sahte_kamu_gorevlisi": "Sahte kamu görevlisi (polis, savcı)", "yatirim_vip_grup": "Yatırım / VIP grup",
    "yasa_disi_bahis": "Yasa dışı bahis", "oyun_hesap_skin": "Oyun hesabı / skin", "odul_kampanya": "Sahte ödül / kampanya",
    "yakin_taklidi": "Yakın taklidi (\"anne, numaram değişti\")", "gorev_is_ilani": "Sahte iş / görev ilanı",
    "reklam_spam": "Reklam", "mesru_islem": "Olağan bildirim",
}


class Ayar:
    def __init__(self):
        e = os.environ.get
        self.llama_url = e("KALKAN_LLAMA_URL", "http://127.0.0.1:8080")
        self.denetim_yol = e("KALKAN_DENETIM_YOL", "logs/denetim.jsonl")
        self.dakika = int(e("KALKAN_LIMIT_DAKIKA", "10"))
        self.gun = int(e("KALKAN_LIMIT_GUN", "200"))
        self.kuyruk = int(e("KALKAN_KUYRUK_MAKS", "4"))
        self.bekleme_sn = float(e("KALKAN_KUYRUK_BEKLEME_SN", "30"))
        self.vekil = e("KALKAN_GUVENILIR_VEKIL", "0") == "1"
        self.zaman_asimi = float(e("KALKAN_MODEL_ZAMAN_ASIMI_SN", "30"))


class HizSiniri:
    """IP başına kayan pencere; bellekte (tek süreç). Eski kayıtlar istek geldikçe atılır."""

    def __init__(self, dakika: int, gun: int):
        self.dakika, self.gun = dakika, gun
        self.k: dict[str, deque] = defaultdict(deque)
        self.kilit = threading.Lock()

    def izin(self, ip: str, simdi: float | None = None) -> tuple[bool, int]:
        simdi = time.time() if simdi is None else simdi
        with self.kilit:
            q = self.k[ip]
            while q and simdi - q[0] > 86400:
                q.popleft()
            son_dk = sum(1 for t in q if simdi - t <= 60)
            if son_dk >= self.dakika:
                return False, int(60 - (simdi - next(t for t in q if simdi - t <= 60))) + 1
            if len(q) >= self.gun:
                return False, int(86400 - (simdi - q[0])) + 1
            q.append(simdi)
            if len(self.k) > 50_000:                     # bellek tavanı: en eski IP'ler atılır
                for eski in list(self.k)[:10_000]:
                    del self.k[eski]
            return True, 0


class Kuyruk:
    """Aynı anda 1 model çağrısı; en çok `maks` bekleyen."""

    def __init__(self, maks: int):
        self.calisan = threading.Semaphore(1)
        self.yer = threading.BoundedSemaphore(maks + 1)

    def __enter__(self):
        if not self.yer.acquire(blocking=False):
            raise HTTPException(503, "Sistem şu an meşgul, lütfen birazdan tekrar deneyin.")
        return self

    def bekle(self, sn: float) -> bool:
        return self.calisan.acquire(timeout=sn)

    def birak(self):
        self.calisan.release()

    def __exit__(self, *a):
        self.yer.release()


class Istek(BaseModel):
    model_config = ConfigDict(extra="forbid")
    mesaj: str = Field(min_length=1)


def uygulama(ayar: Ayar | None = None, arka_uc=None) -> FastAPI:
    ayar = ayar or Ayar()
    arka = arka_uc if arka_uc is not None else OpenAIUyumlu(ayar.llama_url, zaman_asimi=ayar.zaman_asimi)
    hiz, kuyruk, denetci = HizSiniri(ayar.dakika, ayar.gun), Kuyruk(ayar.kuyruk), Denetci(ayar.denetim_yol)
    app = FastAPI(title="Kalkan", version=__version__, docs_url=None, redoc_url=None, openapi_url=None)

    @app.middleware("http")
    async def basliklar(request: Request, call_next):
        r = await call_next(request)
        r.headers["Content-Security-Policy"] = ("default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
                                                "connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'")
        r.headers["X-Content-Type-Options"] = "nosniff"
        r.headers["Referrer-Policy"] = "no-referrer"
        r.headers["X-Frame-Options"] = "DENY"
        r.headers["Cache-Control"] = "no-store"
        return r

    def istemci_ip(request: Request) -> str:
        if ayar.vekil and (xff := request.headers.get("x-forwarded-for")):
            return xff.split(",")[-1].strip()      # son öğe: Caddy'nin gördüğü gerçek bağlantı adresi
        return request.client.host if request.client else "?"

    @app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
    def ana_sayfa():
        return FileResponse(WEB / "index.html", media_type="text/html; charset=utf-8")

    @app.get("/kalkan.js", include_in_schema=False)
    def js():
        return FileResponse(WEB / "kalkan.js", media_type="text/javascript; charset=utf-8")

    @app.get("/kalkan.css", include_in_schema=False)
    def css():
        return FileResponse(WEB / "kalkan.css", media_type="text/css; charset=utf-8")

    @app.api_route("/saglik", methods=["GET", "HEAD"])
    def saglik():
        import json
        import urllib.request
        model = "erisilemiyor"
        try:
            with urllib.request.urlopen(f"{ayar.llama_url}/health", timeout=2) as r:
                model = json.loads(r.read() or b"{}").get("status", "ok")
        except Exception:  # noqa: BLE001
            pass
        return {"durum": "ok", "model": model,
                "surum": {"kalkan": __version__, "politika": POLITIKA_SURUMU, "katman": KATMAN_SURUMU}}

    @app.post("/analiz")
    def analiz_et(istek: Istek, request: Request):      # def → FastAPI iş parçacığı havuzunda (model çağrısı senkron)
        if len(istek.mesaj) > HAM_MAKS:
            raise HTTPException(413, f"Mesaj en fazla {HAM_MAKS} karakter olabilir.")
        izin, kalan = hiz.izin(istemci_ip(request))
        if not izin:
            return JSONResponse({"detail": "Çok fazla istek. Lütfen biraz sonra tekrar deneyin."}, status_code=429,
                                headers={"Retry-After": str(kalan)})
        with kuyruk:
            if not kuyruk.bekle(ayar.bekleme_sn):
                raise HTTPException(503, "Sistem şu an meşgul, lütfen birazdan tekrar deneyin.")
            try:
                t0 = time.perf_counter()
                sonuc, iz = analiz(istek.mesaj, arka, istem="kisa", katman=True)
                sure = (time.perf_counter() - t0) * 1000
            finally:
                kuyruk.birak()
        denetci.yaz(istek.mesaj, sonuc, iz)
        d = sonuc.model_dump(mode="json")
        d["tur_adi"] = TUR_ADI.get(d["tur"]) if d["tur"] else None
        d["gosterilen_metin"] = hazirla(istek.mesaj).maskeli    # kişisel veriler maskeli; kanıt aralıkları buna göre
        d["sure_ms"] = round(sure)
        d["model_kullanildi"] = iz.json_gecerli
        return d

    return app

