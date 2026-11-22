"""Adım 9b · güvenlik: kırpma saldırısı, BYOK anahtarı sızıntısı, metinsiz denetim kaydı (ağ yok / yalnızca 127.0.0.1)."""
import http.server
import json
import os
import stat
import threading
from pathlib import Path

import pytest

from kalkan.backends.openai_compat import Cevap, OpenAIUyumlu
from kalkan.denetim import Denetci, hata_turu, kayit
from kalkan.schema import Risk
from kalkan.service import GIRDI_MAKS, HAM_MAKS, analiz

KOK = Path(__file__).resolve().parents[1]
ANAHTAR = "sk-test-GIZLI-0123456789abcdef"


class Sahte:
    def __init__(self, cikti):
        self.cikti = cikti

    def sohbet(self, sistem, kullanici, sema):
        return Cevap(json.dumps(self.cikti, ensure_ascii=False))


MESRU = Sahte({"kanitlar": [], "tur": "mesru_islem"})
DOLGU = "Değerli müşterimiz, hizmet kalitemizi artırmak için çalışmalarımız sürüyor ve görüşleriniz önemli. " * 25
SALDIRI = "Sarnıçbank: hesabınız askıya alındı. Şifrenizi 2 saat içinde sarnicbank-onay.top adresinde doğrulayın."


# ─── kırpma saldırısı ───────────────────────────────────────────────────────────────────────────────
def test_kirpma_kuyruktaki_dolandiricilik_yakalanir():
    """Model yalnızca ilk 2.000 karakteri görür ve 'meşru' der; kural metnin tamamını görür."""
    ham = DOLGU + SALDIRI
    assert len(ham) > GIRDI_MAKS
    s, iz = analiz(ham, MESRU, istem="kisa", katman=True)
    assert s.risk in (Risk.orta, Risk.yuksek) and s.girdi_kirpildi
    assert len(iz.model_girdisi) <= GIRDI_MAKS and "sarnicbank-onay" not in iz.model_girdisi


def test_kirpilan_zararsiz_metin_dusuk_alamaz():
    s, iz = analiz(DOLGU, MESRU, istem="kisa", katman=True)
    assert s.risk == Risk.belirsiz and s.oneri_kodu == "KIRPILDI_DIKKAT" and iz.katman_kaynak == "kirpildi"


def test_kisa_zararsiz_metin_dusuk_kalir():
    s, _ = analiz("Kargonuz teslim edilmiştir. İyi günler dileriz.", MESRU, istem="kisa", katman=True)
    assert s.risk == Risk.dusuk and not s.girdi_kirpildi


def test_ham_ust_siniri():
    s, iz = analiz("a " * HAM_MAKS, MESRU, istem="kisa", katman=True)
    assert s.girdi_kirpildi and s.risk != Risk.dusuk


# ─── BYOK anahtarı ─────────────────────────────────────────────────────────────────────────────────
class _Yankici(http.server.BaseHTTPRequestHandler):
    """En kötü sağlayıcı: 401 gövdesinde isteğin başlıklarını AYNEN geri yazar."""

    def do_POST(self):
        self.rfile.read(int(self.headers.get("Content-Length", 0)))
        govde = json.dumps({"error": {"message": f"invalid key: {self.headers.get('Authorization')}",
                                      "echo": dict(self.headers)}}).encode()
        self.send_response(401)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(govde)

    def log_message(self, *a):
        pass


@pytest.fixture()
def yankici():
    srv = http.server.HTTPServer(("127.0.0.1", 0), _Yankici)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield f"http://127.0.0.1:{srv.server_port}"
    srv.shutdown()


def test_byok_anahtari_hicbir_ciktida_yok(yankici, capsys, tmp_path):
    arka = OpenAIUyumlu(yankici, model="x", api_key=ANAHTAR, yerel=False)
    s, iz = analiz(SALDIRI, arka, istem="kisa", katman=True)
    d = Denetci(tmp_path / "d.jsonl").yaz(SALDIRI, s, iz)
    yerler = {
        "repr": repr(arka), "vars": str(vars(arka)), "hata": str(iz.hata), "iz": repr(iz),
        "sonuc": s.model_dump_json(), "denetim": json.dumps(d), "dosya": (tmp_path / "d.jsonl").read_text(),
        "ekran": "".join(capsys.readouterr()),
    }
    for ad, metin in yerler.items():
        assert ANAHTAR not in metin, ad
        assert "GIZLI-0123" not in metin, ad
    assert iz.hata and iz.hata.startswith("HTTP 401") and "***" in iz.hata   # hata görünür ama maskeli
    assert s.risk != Risk.dusuk                                             # fail-closed


def test_byok_anahtari_serilestirilemez():
    import pickle
    arka = OpenAIUyumlu("http://127.0.0.1:9", api_key=ANAHTAR, yerel=False)
    with pytest.raises(TypeError):
        pickle.dumps(arka)


def test_byok_anahtari_istisna_metninde_yok():
    arka = OpenAIUyumlu("http://127.0.0.1:9", model="x", api_key=ANAHTAR, yerel=False, zaman_asimi=0.5)
    c = arka.sohbet("s", "k", {})
    assert c.hata and ANAHTAR not in c.hata


# ─── denetim kaydı ─────────────────────────────────────────────────────────────────────────────────
def _pencereler(metin: str, n: int = 10):
    m = " ".join(metin.split())
    return {m[i:i + n] for i in range(0, max(len(m) - n, 0) + 1, 3) if len(m[i:i + n].strip()) == n}


@pytest.mark.parametrize("dosya", ["data/adversarial/adversarial.jsonl", "data/adversarial/kor.jsonl"])
def test_denetim_kaydi_metin_icermez(dosya):
    yol = KOK / dosya
    if not yol.exists():
        pytest.skip(f"{dosya} yok (make veri)")
    for o in map(json.loads, open(yol, encoding="utf-8")):
        # model mesajdan birebir alıntı yapsın: kayda sızarsa yakalansın
        alinti = " ".join(o["model_girdisi"].split())[:30]
        s, iz = analiz(o["metin"], Sahte({"kanitlar": [{"alinti": alinti, "sinyal": "odeme_talebi"}],
                                          "tur": "kurum_taklidi"}), istem="kisa", katman=True)
        satir = json.dumps(kayit(o["metin"], s, iz), ensure_ascii=False)
        sizan = [p for p in _pencereler(o["metin"]) if p in satir]
        assert not sizan, (o["id"], sizan[:3])


def test_denetim_dosyasi_yalnizca_sahibine_acik(tmp_path):
    Denetci(tmp_path / "logs" / "d.jsonl")
    mod = stat.S_IMODE(os.stat(tmp_path / "logs" / "d.jsonl").st_mode)
    assert mod == 0o600, oct(mod)


def test_hata_turu_metin_tasimaz():
    assert hata_turu('sema: 1 validation error … input_value="Anne acil 5000 TL"') == "sema"
    assert hata_turu("HTTP 401: invalid key sk-***") == "http_4xx"
    assert hata_turu("URLError: <urlopen error [Errno 111] Connection refused>") == "baglanti"
    assert hata_turu(None) is None
