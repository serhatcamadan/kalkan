"""KALKAN v1 — iskelet ve spike verisi testleri."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_paket_iceri_aktarilir():
    import kalkan
    assert kalkan.__version__


def test_spike_verisi_kanitlari_birebir(tmp_path):
    spec = importlib.util.spec_from_file_location("msd", ROOT / "training/spike/make_spike_data.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.main(tmp_path)
    for name, n in (("train", 6), ("valid", 2)):
        rows = [json.loads(l) for l in (tmp_path / f"{name}.jsonl").read_text(encoding="utf-8").splitlines()]
        assert len(rows) == n
        for r in rows:
            mesaj = r["messages"][1]["content"]
            cevap = json.loads(r["messages"][2]["content"])
            assert all(k["alinti"] in mesaj for k in cevap["kanitlar"])
            assert "güvenli" not in r["messages"][2]["content"].lower()
