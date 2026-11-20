"""KALKAN v1 — normalize testleri (Türkçe küçük harf tuzakları, ofset koruma)."""
import pytest

from kalkan.normalize import Metin, asciile, kanonik, kucuk, tr_kucuk


def test_AI_iki_ayri_kucuk_harf():
    assert tr_kucuk("AI") == "aı"      # Türkçe: yapay zekâ değil "aı"
    assert kucuk("AI") == "ai"


def test_buyuk_I_noktali_tuzagi():
    assert len("İ".lower()) == 2       # Python'un kendi davranışı: tuzağın kanıtı
    assert tr_kucuk("İADE") == "iade" and len(tr_kucuk("İADE")) == 4
    assert kucuk("İSTANBUL") == "istanbul"
    assert tr_kucuk("IBAN") == "ıban" and kucuk("IBAN") == "iban"
    assert asciile(tr_kucuk("IBAN")) == "iban"   # ascii görünüm ikisini birleştirir


def test_ascii_katlama():
    assert asciile(tr_kucuk("ÇIKIŞ ŞİFRE GÜMRÜK Ödeme")) == "cikis sifre gumruk odeme"


@pytest.mark.parametrize("ham", ["İADE İçin TIKLA", "ﬁnans ０５３２", "ka​rgo‮", "Ödeme\tşimdi\n", "İıIi"])
def test_gorunumler_uzunluk_korur(ham):
    m = Metin(ham)
    assert len({len(m.kanonik), len(m.tr_kucuk), len(m.kucuk), len(m.ascii), len(m.iskelet)}) == 1


def test_kanonik_gorunmezleri_atar_ve_nfkc_uygular():
    assert kanonik("ka​rgo") == "kargo"
    assert kanonik("０５３２") == "0532"          # tam genişlikli rakam
    assert kanonik("a‮b") == "ab"           # sağdan-sola zorlama
    assert kanonik("satır\nsonu") == "satır\nsonu"


def test_iskelet_homoglyph():
    assert Metin("mаvibank").iskelet == "mavibank"   # 2. harf Kiril 'а'
    assert Metin("MAVİBANK").ascii == "mavibank"
