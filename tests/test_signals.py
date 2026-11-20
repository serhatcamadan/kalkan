"""KALKAN v1 — deterministik sinyal testleri. Linkler asla açılmaz."""
from kalkan.normalize import Metin
from kalkan.signals import cikar


def tipler(t):
    return {s.tip for s in cikar(Metin(t))}


def test_defang_link_ve_marka_iceren_yabanci():
    s = cikar(Metin("Hesabınız askıda: hxxps://mavibank-guvenlik[.]top/giris"))
    t = {x.tip for x in s}
    assert {"link", "supheli_tld", "marka_iceren_yabanci"} <= t
    link = next(x for x in s if x.tip == "link")
    assert link.deger == "mavibank-guvenlik.top" and link.ek["defang"]


def test_kisa_link():
    assert {"link", "kisa_link"} <= tipler("Ödeme için bit.ly/abc123")


def test_benzer_ve_homoglyph_alan_adi():
    assert "benzer_alan_adi" in tipler("Giriş: https://mavibnak.com.tr")
    assert "benzer_alan_adi" in tipler("Giriş: https://rnavibank.com")
    t = tipler("Giriş: https://mаvibank.com.tr")          # Kiril 'а'
    assert "unicode_alan_adi" in t and ({"marka_iceren_yabanci", "benzer_alan_adi"} & t)
    assert "punycode" in tipler("Giriş: https://xn--mvibank-2fg.com.tr")


def test_resmi_alan_adi_sadece_bilgi():
    t = tipler("Detay: https://www.mavibank.com.tr/kampanya")
    assert "resmi_alan_adi" in t and "marka_iceren_yabanci" not in t


def test_cumle_ici_nokta_link_degil():
    assert "link" not in tipler("İşleminiz tamamlandı.Lütfen bekleyin. Tutar 1.250,00 TL")


def test_tutarlar():
    s = [x for x in cikar(Metin("49,90 TL, 5.000 TL, ₺1.250,50 ve 7.500 lira; 2026 yılı; 24 saat")) if x.tip == "tutar"]
    assert [x.ek["tl"] for x in s] == [49.9, 5000.0, 1250.5, 7500.0]


def test_otp_ve_paylasma_uyarisi_mesru_ipucu():
    t = tipler("Doğrulama kodunuz 482913. Bu kodu banka çalışanları dahil kimseyle paylaşmayın.")
    assert {"otp", "paylasma_uyarisi"} <= t and "tutar" not in t


def test_iban_sinyali_maskeden_once_gecerlilikle():
    s = [x for x in cikar(Metin("Şu IBAN'a at TR00 0000 0000 0000 0000 0000 00 kimseye söyleme")) if x.tip == "iban"]
    assert len(s) == 1 and s[0].deger == "[IBAN]" and s[0].ek["gecerli"] is False


def test_eposta_link_sanilmaz():
    assert "link" not in tipler("Bize destek@mavibank.com.tr adresinden yazın")


def test_ham_pii_sinyal_degerine_yazilmaz():
    for s in cikar(Metin("Ara 0532 123 45 67")):
        assert "0532" not in s.deger


def test_mesru_uyari_ile_gizlilik_baskisi_karismaz():
    """Yüzeyde benzer, anlamca zıt: v1 taslağında ikisi aynı sinyale düşüyordu."""
    mesru = tipler("Şifreniz 4821. Bu kodu kimseyle paylaşmayın.")
    sahte = tipler("Acil 7.500 TL lazım, kimseye söyleme. Bankayı arama sakın.")
    assert "paylasma_uyarisi" in mesru and "gizlilik_ifadesi" not in mesru
    assert "gizlilik_ifadesi" in sahte and "paylasma_uyarisi" not in sahte


def test_canli_otp_maskelenir_ve_sinyale_sizmaz():
    from kalkan.pii import maskele
    from kalkan.signals import maske_araliklari
    m = Metin("Doğrulama kodunuz 482913. Bu kodu kimseyle paylaşmayın.")
    s = cikar(m)
    assert all("482913" not in x.deger for x in s)
    assert maskele(m.kanonik, maske_araliklari(s)).metin == "Doğrulama kodunuz [OTP]. Bu kodu kimseyle paylaşmayın."
