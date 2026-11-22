"""Adım 10 · API: ürün yolu, sınırlar, hız sınırı, kuyruk, güvenlik başlıkları, metinsiz denetim (ağ yok)."""
import json
import threading
import time

import pytest

fastapi = pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from kalkan.api import Ayar, HizSiniri, uygulama  # noqa: E402
from kalkan.backends.openai_compat import Cevap  # noqa: E402

KARGO = "Kestane Kargo: gönderiniz gümrükte. 49,90 TL ödeyin: kstn-kargo.info/ode 24 saat içinde"


class Sahte:
    def __init__(self, cikti=None, bekle=0.0):
        self.cikti, self.bekle, self.cagri = cikti, bekle, 0

    def sohbet(self, sistem, kullanici, sema):
        self.cagri += 1
        time.sleep(self.bekle)
        if self.cikti is None:
            return Cevap(None, "URLError: bağlantı yok")
        return Cevap(json.dumps(self.cikti, ensure_ascii=False))


def _istemci(tmp_path, arka=None, **ayar):
    a = Ayar()
    a.denetim_yol = str(tmp_path / "denetim.jsonl")
    a.llama_url = "http://127.0.0.1:9"
    for k, v in ayar.items():
        setattr(a, k, v)
    return TestClient(uygulama(a, arka or Sahte({"kanitlar": [{"alinti": "49,90 TL ödeyin", "sinyal": "odeme_talebi"}],
                                                   "tur": "sahte_kargo_gumruk"})))


def test_analiz_urun_yolu(tmp_path):
    c = _istemci(tmp_path)
    r = c.post("/analiz", json={"mesaj": KARGO})
    assert r.status_code == 200
    d = r.json()
    assert d["risk"] == "yuksek" and d["tur"] == "sahte_kargo_gumruk" and d["tur_adi"]
    for k in d["kanitlar"]:
        assert d["gosterilen_metin"][k["bas"]:k["bit"]] == k["alinti"]       # arayüz vurgulaması buna dayanır
    assert "guvenli" not in json.dumps(d, ensure_ascii=False).lower()


def test_pii_gosterilen_metinde_maskeli(tmp_path):
    c = _istemci(tmp_path, Sahte({"kanitlar": [], "tur": "mesru_islem"}))
    d = c.post("/analiz", json={"mesaj": "Anne acil 2.500 lazım TR33 0006 1005 1978 6457 8413 26"}).json()
    assert "TR33" not in d["gosterilen_metin"] and "[IBAN]" in d["gosterilen_metin"]
    assert d["risk"] != "dusuk"


def test_model_yoksa_fail_closed_200(tmp_path):
    c = _istemci(tmp_path, Sahte(None))
    d = c.post("/analiz", json={"mesaj": "Kargonuz teslim edilmiştir. İyi günler."}).json()
    assert d["risk"] == "belirsiz" and d["model_kullanildi"] is False


def test_girdi_sinirlari(tmp_path):
    c = _istemci(tmp_path)
    assert c.post("/analiz", json={"mesaj": ""}).status_code == 422
    assert c.post("/analiz", json={"mesaj": "a" * 10_001}).status_code == 413
    assert c.post("/analiz", json={"mesaj": "x", "fazla": 1}).status_code == 422
    assert c.post("/analiz", content="duz metin", headers={"Content-Type": "text/plain"}).status_code == 422


def test_hiz_siniri_dakika(tmp_path):
    c = _istemci(tmp_path, dakika=3)
    kodlar = [c.post("/analiz", json={"mesaj": KARGO}).status_code for _ in range(5)]
    assert kodlar == [200, 200, 200, 429, 429]
    r = c.post("/analiz", json={"mesaj": KARGO})
    assert int(r.headers["Retry-After"]) > 0


def test_hiz_siniri_pencere_kayar():
    h = HizSiniri(dakika=2, gun=3)
    assert h.izin("a", 0)[0] and h.izin("a", 1)[0] and not h.izin("a", 2)[0]
    assert h.izin("a", 62)[0]                       # dakika geçti
    assert not h.izin("a", 120)[0]                  # günlük 3 doldu
    assert h.izin("b", 2)[0]                        # IP'ler ayrı


def test_xff_yalnizca_guvenilir_vekilde(tmp_path):
    c = _istemci(tmp_path, dakika=1)
    ilk = c.post("/analiz", json={"mesaj": KARGO}, headers={"X-Forwarded-For": "1.1.1.1"})
    ikinci = c.post("/analiz", json={"mesaj": KARGO}, headers={"X-Forwarded-For": "2.2.2.2"})
    assert ilk.status_code == 200 and ikinci.status_code == 429      # başlık taklidiyle sınır aşılamaz
    c2 = _istemci(tmp_path, dakika=1, vekil=True)
    assert c2.post("/analiz", json={"mesaj": KARGO}, headers={"X-Forwarded-For": "1.1.1.1"}).status_code == 200
    assert c2.post("/analiz", json={"mesaj": KARGO}, headers={"X-Forwarded-For": "2.2.2.2"}).status_code == 200


def test_kuyruk_dolunca_503(tmp_path):
    arka = Sahte({"kanitlar": [], "tur": "mesru_islem"}, bekle=0.4)
    c = _istemci(tmp_path, arka, kuyruk=1, dakika=100)
    kodlar = []
    def istek():
        kodlar.append(c.post("/analiz", json={"mesaj": "Kargonuz teslim edildi."}).status_code)
    ts = [threading.Thread(target=istek) for _ in range(4)]
    for t in ts:
        t.start()
        time.sleep(0.02)
    for t in ts:
        t.join()
    assert kodlar.count(503) >= 1 and kodlar.count(200) >= 2, kodlar


def test_guvenlik_basliklari_ve_arayuz(tmp_path):
    c = _istemci(tmp_path)
    r = c.get("/")
    assert r.status_code == 200 and "Mesajı kontrol et" in r.text
    csp = r.headers["content-security-policy"]
    assert "script-src 'self'" in csp and "unsafe-inline" not in csp and "frame-ancestors 'none'" in csp
    assert r.headers["x-content-type-options"] == "nosniff" and r.headers["referrer-policy"] == "no-referrer"
    assert "<script>" not in r.text and "<style>" not in r.text          # satır içi kod yok (CSP)
    js = c.get("/kalkan.js").text
    assert ".innerHTML" not in js and "insertAdjacentHTML" not in js                                          # kullanıcı metni yalnızca textContent
    assert c.get("/kalkan.css").status_code == 200
    assert c.get("/docs").status_code == 404 and c.get("/openapi.json").status_code == 404


def test_saglik_model_yok(tmp_path):
    d = _istemci(tmp_path).get("/saglik").json()
    assert d["durum"] == "ok" and d["model"] == "erisilemiyor" and d["surum"]["katman"]


def test_denetim_metinsiz(tmp_path, capsys):
    c = _istemci(tmp_path)
    c.post("/analiz", json={"mesaj": KARGO})
    satir = (tmp_path / "denetim.jsonl").read_text(encoding="utf-8")
    assert "Kestane" not in satir and "49,90" not in satir and "kstn-kargo" not in satir
    assert "Kestane" not in "".join(capsys.readouterr())
