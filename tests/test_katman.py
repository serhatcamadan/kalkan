"""Adım 9a · katmanlı karar (ADR-0006): kurallar + "ölçülen = çalışan" tekrar oynatma testi."""
import json
import random
from pathlib import Path

import pytest

from kalkan.backends.openai_compat import Cevap
from kalkan.katman import katmanla
from kalkan.policy import Karar
from kalkan.schema import DogrulanmisKanit, Risk, Sinyal, Tur
from kalkan.service import analiz

KOK = Path(__file__).resolve().parents[1]


def _k(risk):
    return Karar(risk, "X", "Bu mesajda dikkat gerektiren işaretler var.", [])


def _kanit(sinyal, alinti="abc"):
    return DogrulanmisKanit(alinti=alinti, sinyal=Sinyal(sinyal), bas=0, bit=len(alinti))


def test_model_riski_asla_dusurmez():
    for r in (Risk.orta, Risk.yuksek, Risk.belirsiz):
        k = katmanla(_k(r), Tur.kurum_taklidi, [], Tur.mesru_islem, [], model_cevap_verdi=True)
        assert k.karar.risk == r and k.kaynak == "kural"


def test_kural_dusuk_model_yok_belirsiz():
    k = katmanla(_k(Risk.dusuk), Tur.mesru_islem, [], None, [], model_cevap_verdi=False)
    assert k.karar.risk == Risk.belirsiz and k.kaynak == "model_yok"


def test_yukseltme_talepli_iki_kanit_ister():
    iki_talepli = [_kanit("odeme_talebi", "50 TL ödeyin"), _kanit("link", "bit.ly/x")]
    k = katmanla(_k(Risk.dusuk), Tur.mesru_islem, [], Tur.sahte_kargo_gumruk, iki_talepli, model_cevap_verdi=True)
    assert k.karar.risk == Risk.orta and k.tur == Tur.sahte_kargo_gumruk and k.kaynak == "model_ikinci_gorus"
    tek = katmanla(_k(Risk.dusuk), Tur.mesru_islem, [], Tur.sahte_kargo_gumruk, iki_talepli[:1], model_cevap_verdi=True)
    talepsiz = katmanla(_k(Risk.dusuk), Tur.mesru_islem, [], Tur.sahte_kargo_gumruk,
                        [_kanit("aciliyet"), _kanit("link")], model_cevap_verdi=True)
    mesru = katmanla(_k(Risk.dusuk), Tur.mesru_islem, [], Tur.mesru_islem, iki_talepli, model_cevap_verdi=True)
    assert tek.karar.risk == talepsiz.karar.risk == mesru.karar.risk == Risk.dusuk


class Tekrar:
    """Kaydedilmiş model çıktılarını mesaj → JSON olarak geri oynatan arka uç (ağ yok)."""

    def __init__(self, harita: dict[str, str | None]):
        self.harita = harita

    def sohbet(self, sistem, kullanici, sema):
        metin = self.harita.get(kullanici)
        return Cevap(metin=metin, hata=None if metin is not None else "kayit_yok")


def _tekrar_oyna(kayit: dict):
    """Servis (katman=True) ile eval/katmanli.py ★ aynı riski üretmeli: ölçülen = çalışan."""
    from eval.katmanli import SECILEN, birlestir, karar
    from eval.yeniden_puanla import satirlar
    from kalkan.injection import sarmala
    from kalkan.service import hazirla, kural_karari

    rows = {o["id"]: o for o in satirlar(kayit["meta"])}
    harita, beklenen = {}, {}
    for t in kayit["tahminler"]:
        o = rows.get(t["id"])
        if o is None:
            pytest.skip("sonuç dosyası güncel veriyle eşleşmiyor")
        h = hazirla(o["metin"])
        harita[sarmala(h.maskeli)] = (json.dumps({"kanitlar": t["kanitlar"], "tur": t["tur"]}, ensure_ascii=False)
                                      if t.get("json_gecerli", True) and t.get("tur") else "BOZUK")
        kk, kt, kg = kural_karari(h)
        beklenen[t["id"]] = birlestir(SECILEN, (kk.risk.value, kt.value, kg, kk), karar(h, t))[0]
    arka = Tekrar(harita)
    farkli, kaynak = [], {}
    for i, o in rows.items():
        if i in beklenen:
            s, iz = analiz(o["metin"], arka, istem="kisa", katman=True)
            kaynak[iz.katman_kaynak] = kaynak.get(iz.katman_kaynak, 0) + 1
            if s.risk.value != beklenen[i]:
                farkli.append(i)
    assert not farkli, farkli[:5]
    return kaynak


def test_servis_eval_ile_ayni_karari_verir_sentetik():
    """Kural sonuçlarından türetilmiş, yükseltme yollarını zorlayan sahte bir 'model' ile."""
    yol = KOK / "eval/results/kural__golden.json"
    if not yol.exists():
        pytest.skip("kural__golden.json yok (make eval)")
    from eval.yeniden_puanla import satirlar
    from kalkan.service import hazirla
    kayit = json.loads(yol.read_text(encoding="utf-8"))
    rows = {o["id"]: o for o in satirlar(kayit["meta"])}
    r = random.Random(7)
    for t in kayit["tahminler"]:
        t["json_gecerli"] = True
        x = r.random()
        if x < 0.25:                      # model dolandırıcılık + mesajda birebir geçen 2 kanıt (biri talep)
            mg = hazirla(rows[t["id"]]["metin"]).maskeli
            t["tur"] = "sahte_kargo_gumruk"
            t["kanitlar"] = [{"alinti": mg[:12], "sinyal": "odeme_talebi"}, {"alinti": mg[12:24], "sinyal": "link"}]
        elif x < 0.35:                    # model bozuk cevap → fail-closed yolu
            t["json_gecerli"] = False
    kaynak = _tekrar_oyna(kayit)
    assert kaynak.get("model_ikinci_gorus", 0) > 0 and kaynak.get("model_yok", 0) > 0, kaynak


@pytest.mark.parametrize("ad", ["ft-0.8b-v3-Q8_0__golden.json", "ft-0.8b-v3-Q8_0__dogrulama.json",
                                "ft-0.8b-v3-Q8_0__adversarial.json"])
def test_servis_eval_ile_ayni_karari_verir_gercek(ad):
    yol = KOK / "eval/results" / ad
    if not yol.exists():
        pytest.skip(f"{ad} yok")
    _tekrar_oyna(json.loads(yol.read_text(encoding="utf-8")))


def test_kural_paketi_eski_sonuclarla_ayni():
    """kalkan/kural.py'ye taşıma davranışı değiştirmedi (Adım 4–8 kural sonuçlarıyla birebir)."""
    from eval.modeller.kural import KuralModeli
    from eval.yeniden_puanla import satirlar
    yol = KOK / "eval/results/kural__golden.json"
    if not yol.exists():
        pytest.skip("kural__golden.json yok")
    r = json.loads(yol.read_text(encoding="utf-8"))
    rows = {o["id"]: o for o in satirlar(r["meta"])}
    km = KuralModeli()
    for t in r["tahminler"]:
        y = km.tahmin(rows[t["id"]])
        assert (y.tur, y.kanitlar) == (t["tur"], t["kanitlar"]), t["id"]
