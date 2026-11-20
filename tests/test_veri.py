"""KALKAN v1 — üretilmiş veri setinin değişmezleri (data/splits, data/adversarial)."""
import json
import re
from pathlib import Path

import pytest
import yaml

from kalkan.schema import ModelCiktisi
from kalkan.taxonomy import yukle

KOK = Path(__file__).resolve().parents[1]
SPLITS = ["egitim", "dogrulama", "test"]


def oku(p):
    return [json.loads(x) for x in open(KOK / p, encoding="utf-8")]


@pytest.fixture(scope="module")
def veri():
    return {s: oku(f"data/splits/{s}.jsonl") for s in SPLITS}


def test_hedefler_sema_gecerli_ve_alintilar_birebir(veri):
    for rows in veri.values():
        for r in rows:
            h = ModelCiktisi.model_validate(r["hedef"])
            for k in h.kanitlar:
                assert k.alinti in r["model_girdisi"], (r["id"], k.alinti)
            assert "\\u" not in h.kompakt_json()          # Türkçe harf kaçışı token'ı ~2 katına çıkarır


def test_sablon_ve_marka_bolumleri_ayrik(veri):
    for a, b in [("egitim", "dogrulama"), ("egitim", "test"), ("dogrulama", "test")]:
        assert not ({r["sablon_id"] for r in veri[a]} & {r["sablon_id"] for r in veri[b]})
        assert not ({r["marka"] for r in veri[a]} & {r["marka"] for r in veri[b]})
        assert not ({r["metin"] for r in veri[a]} & {r["metin"] for r in veri[b]})


def test_model_girdisinde_ham_pii_yok(veri):
    for rows in veri.values():
        for r in rows:
            g = r["model_girdisi"]
            assert not re.search(r"TR\d{2}[ ]?\d{4}", g), r["id"]
            assert not re.search(r"(?<![\d.])(\+90|0)?\s*599\s*\d{3}", g), r["id"]   # üretilen telefonlar 0599…


def test_tur_dengesi(veri):
    from collections import Counter
    c = Counter(r["tur"] for r in veri["egitim"])
    assert len(c) == 11 and max(c.values()) - min(c.values()) <= 2


def test_havuz_markalari_taksonomide():
    from tools.veri_uret import slug
    kay = yaml.safe_load(open(KOK / "data/templates/sablonlar.yaml", encoding="utf-8"))
    tax = yukle()["kurgusal_markalar"]
    for h in kay["havuzlar"].values():
        for kat, liste in h.items():
            if kat != "bahis":
                assert all(slug(m) in tax for m in liste), liste


def test_adversarial_alanlari():
    adv = oku("data/adversarial/adversarial.jsonl")
    assert len(adv) >= 30 and len({a["id"] for a in adv}) == len(adv)
    turler = {t["id"] for t in yukle()["turler"]}
    for a in adv:
        assert set(a["beklenen_turler"]) <= turler and isinstance(a["asla_dusuk"], bool)
