"""KALKAN v1 — eval metrikleri ve taban çizgisi modellerinin sözleşmesi."""
import json
from pathlib import Path

from eval.metrics import Tahmin, degerlendir, dolandiricilik_mi, ikili_metrikler, kanit_eslesir, tur_metrikleri
from eval.modeller.kural import KuralModeli

KOK = Path(__file__).resolve().parents[1]


def test_belirsiz_fail_closed_alarm_sayilir():
    assert dolandiricilik_mi(None) and dolandiricilik_mi("kurum_taklidi") and not dolandiricilik_mi("mesru_islem")
    m = ikili_metrikler([True, False], [dolandiricilik_mi(None), dolandiricilik_mi(None)])
    assert m["dolandiricilik_recall"] == 1.0 and m["mesru_fpr"] == 1.0


def test_tur_makro_f1_yalnizca_gorulen_siniflar():
    m = tur_metrikleri(["reklam_spam", "mesru_islem"], ["reklam_spam", "reklam_spam"])
    assert m["dogruluk"] == 0.5 and set(m["sinif"]) == {"reklam_spam", "mesru_islem"}
    assert m["en_cok_karisan"][0] == {"altin": "mesru_islem", "tahmin": "reklam_spam", "n": 1}


def test_kanit_eslesme_kurallari():
    g = {"alinti": "24 saat içinde ödeyin", "sinyal": "aciliyet"}
    assert kanit_eslesir({"alinti": "24 saat içinde", "sinyal": "aciliyet"}, g)          # içerme
    assert not kanit_eslesir({"alinti": "24 saat içinde", "sinyal": "odeme_talebi"}, g)  # sinyal farklı
    assert kanit_eslesir({"alinti": "24 SAAT ICINDE odeyin lutfen", "sinyal": "aciliyet"}, g)  # Jaccard


def test_kapi_oncesi_gecerlilik_uydurma_alintiyi_yakalar():
    o = [{"model_girdisi": "Paketiniz gümrükte, 49 TL ödeyin", "tur": "sahte_kargo_gumruk",
          "hedef": {"kanitlar": [{"alinti": "49 TL ödeyin", "sinyal": "odeme_talebi"}]}}]
    t = [Tahmin("sahte_kargo_gumruk", [{"alinti": "49 TL ödeyin", "sinyal": "odeme_talebi"},
                                       {"alinti": "uydurulmuş alıntı", "sinyal": "aciliyet"}])]
    m = degerlendir("golden", o, t)
    assert m["kapi_oncesi_gecerlilik"] == 0.5 and m["eslesme_p"] == 0.5 and m["eslesme_r"] == 1.0


def test_kural_modeli_alintilari_daima_birebir():
    model = KuralModeli()
    for satir in list(open(KOK / "data/splits/dogrulama.jsonl", encoding="utf-8"))[:60]:
        o = json.loads(satir)
        for k in model.tahmin(o).kanitlar:
            assert k["alinti"] in o["model_girdisi"] and len(k["alinti"]) <= 80
