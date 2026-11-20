"""KALKAN v1 — taksonomi YAML ↔ şema enum'ları senkron mu?"""
from kalkan.schema import Risk, Sinyal, Tur
from kalkan.taxonomy import yukle


def test_turler_senkron():
    assert [t["id"] for t in yukle()["turler"]] == [t.value for t in Tur]


def test_sinyaller_senkron():
    assert [s["id"] for s in yukle()["sinyaller"]] == [s.value for s in Sinyal]


def test_riskler_senkron():
    assert yukle()["risk_seviyeleri"] == [r.value for r in Risk]


def test_karisir_gecerli_tur():
    ids = {t["id"] for t in yukle()["turler"]}
    for t in yukle()["turler"]:
        assert t["karisir"] is None or t["karisir"] in ids
