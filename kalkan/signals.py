"""KALKAN · signals.py — deterministik (kural tabanlı) sinyaller       v1 · 2026-11-19

Modelden BAĞIMSIZ, kanonik metin üzerinde, PII maskelemeden ÖNCE çalışır (ADR-0003).
Hiçbir link açılmaz/ziyaret edilmez; yalnızca metin olarak incelenir.

Üretilen sinyal tipleri:
  link                    her bağlantı (defang edilmiş biçimler dahil: hxxp, [.] , (.) , [dot])
  kisa_link               bit.ly vb. kısaltıcı
  punycode                xn-- etiketi
  unicode_alan_adi        alan adında ASCII dışı karakter (homoglyph riski)
  supheli_tld             .top, .xyz … (taksonomideki liste)
  marka_iceren_yabanci    alan adı marka adını içeriyor ama markanın resmi alanı değil
  benzer_alan_adi         marka adına 1–2 harf uzaklıkta (mavibnak, rnavibank)
  resmi_alan_adi          markanın kayıtlı alanı (bilgi amaçlı; tek başına güven gerekçesi DEĞİL)
  iban                    TR IBAN (ek.gecerli = mod-97)
  tutar                   para tutarı (ek.tl = sayısal değer)
  otp                     doğrulama/şifre kodu bağlamında 4–8 haneli sayı
  paylasma_uyarisi        "kodu kimseyle paylaşmayın" → meşru bildirim işareti
  gizlilik_ifadesi        "kimseye söyleme", "bankayı arama" → dolandırıcılık işareti (yukarıdakinin zıddı)
  telefon                 telefon numarası (değer maskeli)
"""
from __future__ import annotations

import re

from . import pii
from .normalize import BENZER, Metin, asciile
from .schema import DeterministikSinyal
from .taxonomy import yukle

_HARF = r"0-9A-Za-zÀ-ɏͰ-ϿЀ-ӿ"
_ETIKET = rf"[{_HARF}](?:[{_HARF}-]{{0,61}}[{_HARF}])?"
_AYRAC = r"(?:\.|\[\.\]|\(\.\)|\[dot\]|\(dot\))"
_URL = re.compile(
    rf"(?<![@\w])(?P<sema>(?:h[tx]{{2}}ps?)://)?(?P<host>{_ETIKET}(?:{_AYRAC}{_ETIKET})+)(?::\d{{1,5}})?(?P<yol>/[^\s]*)?",
    re.IGNORECASE,
)
_BILINEN_TLD = {"com", "net", "org", "tr", "io", "co", "me", "info", "biz", "app", "dev", "ly", "gl", "gd", "at",
                "ws", "ru", "de", "ae", "cc", "su", "id", "us", "uk", "eu", "link", "page", "ai"}
_IKILI_SONEK = {"com.tr", "gov.tr", "org.tr", "net.tr", "edu.tr", "k12.tr", "bel.tr", "av.tr", "gen.tr",
                "biz.tr", "info.tr", "web.tr", "tsk.tr", "pol.tr", "co.uk"}

_TUTAR = re.compile(
    r"(?<![\d.,])(?P<on>₺\s?)?(?P<sayi>\d{1,3}(?:\.\d{3})+|\d+)(?:,(?P<kurus>\d{1,2}))?\s?(?P<birim>TL|TRY|₺|lira)?(?![\w])",
    re.IGNORECASE,
)
_OTP_SAYI = re.compile(r"(?<![\d.,])\d{4,8}(?![\d.,]?\d)")
_OTP_BAGLAM = re.compile(r"\b(kod|kodu|kodunuz|sifre|sifreniz|sifresi|dogrulama|onay|otp|parola|code|guard)\b")
# Meşru uyarı: KOD/ŞİFRE + "kimseyle paylaşmayın". Gizlilik baskısı: "kimseye söyleme", "bankayı arama".
# İkisi yüzeyde benzer ama ANLAMLARI ZIT (ilki meşruiyet işareti, ikincisi dolandırıcılık işareti).
_PAYLASMA = re.compile(r"(kod\w*|sifre\w*|parola\w*).{0,60}(kimse(yle|ye)|ucuncu kisi\w*).{0,30}(paylasma\w*|vermeyin\w*|iletmeyin\w*)"
                       r"|(kimse(yle|ye)).{0,30}(paylasma\w*).{0,40}(kod\w*|sifre\w*)")
_GIZLILIK = re.compile(r"kimseye (soyleme\w*|bahsetme\w*|anlatma\w*)|aramizda kalsin|"
                       r"banka\w* (haber verme\w*|arama\w*|gitme\w*)|polise (haber verme\w*|gitme\w*)")


def _rakamsiz(s: str) -> str:
    """Metin sinyallerinin değerine kod/numara sızmasın."""
    return re.sub(r"\d", "*", s)


def maske_araliklari(sinyaller: list[DeterministikSinyal]) -> list[tuple[str, int, int]]:
    """pii.maskele(..., ek_araliklar=) için: OTP gibi PII-dışı ama gizli kalması gereken aralıklar."""
    return [("OTP", s.bas, s.bit) for s in sinyaller if s.tip == "otp"]


def _refang(host: str) -> str:
    return re.sub(r"\[\.\]|\(\.\)|\[dot\]|\(dot\)", ".", host, flags=re.IGNORECASE).lower()


def _kayitli_etiket(host: str) -> tuple[str, str]:
    """(kayıt edilebilir ana etiket, sonek) → 'mavibank-guvenlik.top' → ('mavibank-guvenlik', 'top')."""
    parca = host.split(".")
    if len(parca) >= 3 and ".".join(parca[-2:]) in _IKILI_SONEK:
        return parca[-3], ".".join(parca[-2:])
    return (parca[-2] if len(parca) >= 2 else parca[0]), parca[-1]


def _iskelet(s: str) -> str:
    return asciile(s.lower()).translate(BENZER).replace("rn", "m").replace("vv", "w")


def _levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    onceki = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        simdi = [i]
        for j, cb in enumerate(b, 1):
            simdi.append(min(onceki[j] + 1, simdi[j - 1] + 1, onceki[j - 1] + (ca != cb)))
        onceki = simdi
    return onceki[-1]


def _link_sinyalleri(m: re.Match, tax: dict) -> list[DeterministikSinyal]:
    host = _refang(m.group("host"))
    tld = host.rsplit(".", 1)[-1]
    kisa = host in set(tax["kisa_link_alanlari"])
    supheli = tld in set(tax["supheli_tld"])
    if not (m.group("sema") or kisa or supheli or tld in _BILINEN_TLD or m.group("yol")):
        return []  # "işlem.Lütfen" gibi cümle içi noktalar link değildir
    if tld.isdigit():
        return []
    b, e = m.start(), m.end()
    defang = host != m.group("host").lower()
    out = [DeterministikSinyal(tip="link", deger=host, bas=b, bit=e, ek={"defang": defang})]
    if kisa:
        out.append(DeterministikSinyal(tip="kisa_link", deger=host, bas=b, bit=e))
    if any(p.startswith("xn--") for p in host.split(".")):
        out.append(DeterministikSinyal(tip="punycode", deger=host, bas=b, bit=e))
    if not host.isascii():
        out.append(DeterministikSinyal(tip="unicode_alan_adi", deger=host, bas=b, bit=e))
    if supheli:
        out.append(DeterministikSinyal(tip="supheli_tld", deger=tld, bas=b, bit=e))

    etiket, _ = _kayitli_etiket(host)
    duz = asciile(etiket.lower()).replace("-", "")       # harfiyen
    isk = _iskelet(etiket).replace("-", "")              # görsel iskelet (rn→m, Kiril а→a, 0→o)
    for marka, resmi in tax["kurgusal_markalar"].items():
        m_isk = _iskelet(marka).replace("-", "")
        if any(host == r or host.endswith("." + r) for r in resmi):
            out.append(DeterministikSinyal(tip="resmi_alan_adi", deger=marka, bas=b, bit=e))
        elif m_isk in duz:
            out.append(DeterministikSinyal(tip="marka_iceren_yabanci", deger=marka, bas=b, bit=e,
                                           ek={"alan": host, "resmi": resmi}))
        elif m_isk in isk or (len(m_isk) >= 5 and _levenshtein(isk, m_isk) <= 2):  # taklit: görünüşte aynı
            out.append(DeterministikSinyal(tip="benzer_alan_adi", deger=marka, bas=b, bit=e,
                                           ek={"alan": host, "resmi": resmi}))
    return out


def cikar(metin: Metin, tax: dict | None = None) -> list[DeterministikSinyal]:
    tax = tax or yukle()
    k, a = metin.kanonik, metin.ascii
    out: list[DeterministikSinyal] = []

    pii_bulgular = pii.bul(k)
    pii_araliklari = [(p.bas, p.bit) for p in pii_bulgular]
    ic = lambda s, e: any(ps <= s and e <= pe for ps, pe in pii_araliklari)  # noqa: E731

    for m in _URL.finditer(k):
        if not ic(m.start(), m.end()):
            out += _link_sinyalleri(m, tax)
    link_araliklari = [(s.bas, s.bit) for s in out if s.tip == "link"]
    linkte = lambda s, e: any(ls <= s and e <= le for ls, le in link_araliklari)  # noqa: E731

    for p in pii_bulgular:
        if p.tip == "IBAN":
            out.append(DeterministikSinyal(tip="iban", deger="[IBAN]", bas=p.bas, bit=p.bit, ek={"gecerli": p.gecerli}))
        elif p.tip == "TEL":
            out.append(DeterministikSinyal(tip="telefon", deger="[TEL]", bas=p.bas, bit=p.bit))

    for m in _TUTAR.finditer(k):
        if not (m.group("on") or m.group("birim")):
            continue  # birimsiz sayı tutar değildir
        if ic(m.start(), m.end()) or linkte(m.start(), m.end()):
            continue
        tl = float(m.group("sayi").replace(".", "") + "." + (m.group("kurus") or "0"))
        out.append(DeterministikSinyal(tip="tutar", deger=m.group().strip(), bas=m.start(), bit=m.end(), ek={"tl": tl}))

    for m in _OTP_SAYI.finditer(k):
        if ic(m.start(), m.end()) or linkte(m.start(), m.end()):
            continue
        pencere = a[max(0, m.start() - 40): m.end() + 25]
        if _OTP_BAGLAM.search(pencere) and not re.search(r"\b(tl|try|lira)\b", a[m.end():m.end() + 5]):
            out.append(DeterministikSinyal(tip="otp", deger="*" * len(m.group()), bas=m.start(), bit=m.end()))

    for m in _PAYLASMA.finditer(a):
        out.append(DeterministikSinyal(tip="paylasma_uyarisi", deger=_rakamsiz(k[m.start():m.end()]), bas=m.start(), bit=m.end()))
    for m in _GIZLILIK.finditer(a):
        out.append(DeterministikSinyal(tip="gizlilik_ifadesi", deger=_rakamsiz(k[m.start():m.end()]), bas=m.start(), bit=m.end()))

    return sorted(out, key=lambda s: (s.bas, s.tip))
