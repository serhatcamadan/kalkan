"""KALKAN v1 — PII testleri. Tüm numaralar algoritmayla üretilmiş SAHTE değerlerdir."""
import random

import pytest

from kalkan.pii import bul, iban_gecerli, luhn_gecerli, maskele, tckn_gecerli

GECERLI_TCKN = "10000000146"          # bilinen test numarası (kontrol haneleri tutar)
GECERLI_KART = "4111 1111 1111 1111"   # standart test kartı (Luhn geçerli)


def iban_uret(govde22: str) -> str:
    for kk in range(100):
        aday = f"TR{kk:02d}{govde22}"
        if iban_gecerli(aday):
            return aday
    raise AssertionError


def test_tckn_kontrol():
    assert tckn_gecerli(GECERLI_TCKN)
    assert not tckn_gecerli("10000000147")
    assert not tckn_gecerli("01234567890")


def test_tckn_rastgele_gecme_orani_yaklasik_yuzde1():
    rnd = random.Random(0)
    n = 20000
    gecen = sum(tckn_gecerli(str(rnd.randint(10**10, 10**11 - 1))) for _ in range(n))
    assert 0.005 < gecen / n < 0.015


def test_luhn():
    assert luhn_gecerli("4111111111111111")
    assert not luhn_gecerli("4111111111111112")


def test_iban():
    i = iban_uret("0006100519786457841326")
    assert iban_gecerli(i) and iban_gecerli(" ".join(i[j:j + 4] for j in range(0, 26, 4)))
    assert not iban_gecerli("TR000006100519786457841326") or i == "TR000006100519786457841326"


def test_maskeleme_hepsi_bir_arada():
    iban = iban_uret("0001000000000000000001")
    iban_bosluklu = " ".join(iban[j:j + 4] for j in range(0, 26, 4))
    t = (f"TC: {GECERLI_TCKN}, kart {GECERLI_KART}, IBAN {iban_bosluklu}, "
         f"tel 0532 123 45 67, +90 212 555 12 34, 444 1 234, posta ali.veli@ornek.com.tr")
    m = maskele(t)
    assert m.metin == ("TC: [TCKN], kart [KART], IBAN [IBAN], tel [TEL], [TEL], [TEL], posta [EPOSTA]")
    for rakam in ("10000000146", "4111", "0532", "ali.veli"):
        assert rakam not in m.metin


def test_gecersiz_iban_yine_maskelenir_ama_isaretlenir():
    b = bul("TR00 0000 0000 0000 0000 0000 00")
    assert [x.tip for x in b] == ["IBAN"] and b[0].gecerli is False


@pytest.mark.parametrize("t", ["Sipariş no 12345678901 hazır", "Doğrulama kodunuz 482913", "%340 kazanç", "49,90 TL"])
def test_pii_olmayan_sayilar_maskelenmez(t):
    assert maskele(t).metin == t


def test_maske_ofset_geri_esleme():
    t = f"Ara: 0532 123 45 67 hemen, kimlik {GECERLI_TCKN} gönder"
    m = maskele(t)
    alinti = "hemen, kimlik [TCKN] gönder"
    bas = m.metin.index(alinti)
    kb, kbit = m.kanonige(bas, bas + len(alinti))
    assert t[kb:kbit] == f"hemen, kimlik {GECERLI_TCKN} gönder"
    bas2 = m.metin.index("[TEL]")                 # etiketin kendisi → orijinal numara
    assert t[slice(*m.kanonige(bas2, bas2 + 5))] == "0532 123 45 67"
