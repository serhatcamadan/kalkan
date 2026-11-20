"""KALKAN v1 — şema testleri."""
import json

import pytest
from pydantic import ValidationError

from kalkan.schema import KANIT_MAKS, ModelCiktisi, Risk, SistemCevabi, yasak_ifade_var


def test_kompakt_json_ve_alan_sirasi():
    c = ModelCiktisi.model_validate({"kanitlar": [{"alinti": "24 saat içinde", "sinyal": "aciliyet"}],
                                     "tur": "sahte_kargo_gumruk"})
    s = c.kompakt_json()
    assert " " not in s.replace("24 saat içinde", "") and "\n" not in s
    assert s.index("kanitlar") < s.index("tur")          # kanıt önce
    assert "içinde" in s                                  # ensure_ascii=False


@pytest.mark.parametrize("bozuk", [
    {"kanitlar": [], "tur": "bilinmeyen"},
    {"kanitlar": [{"alinti": "x" * 81, "sinyal": "link"}], "tur": "reklam_spam"},
    {"kanitlar": [{"alinti": "ab", "sinyal": "link"}] * (KANIT_MAKS + 1), "tur": "reklam_spam"},
    {"kanitlar": [{"alinti": "ab", "sinyal": "uydurma"}], "tur": "reklam_spam"},
    {"kanitlar": [], "tur": "reklam_spam", "risk": "dusuk"},     # model risk üretemez
])
def test_bozuk_model_ciktisi_reddedilir(bozuk):
    with pytest.raises(ValidationError):
        ModelCiktisi.model_validate(bozuk)


def test_llm_semasi_kisitlari_tasir():
    sch = json.dumps(ModelCiktisi.llm_json_schema())
    assert '"maxLength": 80' in sch and '"maxItems": 3' in sch


@pytest.mark.parametrize("metin", ["Bu mesaj güvenli.", "GÜVENLİDİR", "Endişe etmeyin", "Sorun yok", "zararsız görünüyor"])
def test_guvenli_kelimesi_yasak(metin):
    assert yasak_ifade_var(metin)
    with pytest.raises(ValidationError):
        SistemCevabi(trace_id="t", risk=Risk.dusuk, tur=None, oneri_kodu="x", mesaj=metin)


def test_izinli_dusuk_risk_metni():
    SistemCevabi(trace_id="t", risk=Risk.dusuk, tur=None, oneri_kodu="ISARET_YOK",
                 mesaj="Belirgin bir dolandırıcılık işareti bulunamadı. Emin değilseniz kurumu resmi numarasından arayın.")
