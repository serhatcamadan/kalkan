"""KALKAN · pii.py — kişisel veri tespiti ve maskeleme              v1.1 · 2026-11-20

v1.1: ayraçlarda 2 boşluğa/sekmeye kadar tolerans ("0599  885 86 14" maskelenmiyordu; veri testi yakaladı).

Kanonik metin üzerinde çalışır (normalize.Metin.kanonik). Modele, loglara ve denetim kaydına
yalnızca MASKELİ metin gider. Sıra (ADR-0003): önce signals.py sinyalleri çıkarır (IBAN geçerliliği
gibi), SONRA burada maskelenir.

Etiketler ve doğrulama:
  [IBAN]   TR + 24 hane, mod-97 kontrolü (geçersiz IBAN da maskelenir: biçimi zaten hesap no)
  [KART]   13–19 hane, Luhn geçerliyse
  [TCKN]   11 hane, ilk hane ≠ 0, resmi iki kontrol hanesi tutuyorsa
  [TEL]    TR cep/sabit/0850/444 biçimleri
  [EPOSTA]
  [OTP]    signals.py'nin bulduğu doğrulama kodu aralıkları (ek_araliklar ile verilir). Kullanıcının
           yapıştırdığı CANLI bir kod BYOK sağlayıcısına veya loglara gitmemeli.
Çakışmada öncelik: IBAN > KART > TCKN > TEL > EPOSTA (IBAN içindeki rakamlar kart sanılmasın).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

_IBAN = re.compile(r"\bTR(?:[ \t]{0,2}\d){24}\b", re.IGNORECASE)
_KART = re.compile(r"(?<![\d])(?:\d(?:[ \t]{1,2}|-)?){12,18}\d(?![\d])")
_TCKN = re.compile(r"(?<![\d])[1-9]\d{10}(?![\d])")
_TEL = re.compile(
    r"(?<![\d+])(?:\+90[ \t]{0,2}|0090[ \t]{0,2}|0)?\(?[2-58]\d{2}\)?(?:[ \t]{1,2}|-)?\d{3}(?:[ \t]{1,2}|-)?\d{2}(?:[ \t]{1,2}|-)?\d{2}(?![\d])"
    r"|(?<![\d])444[ \t]{0,2}\d[ \t]{0,2}\d{3}(?![\d])"
)
_EPOSTA = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")

ONCELIK = ["IBAN", "KART", "TCKN", "TEL", "EPOSTA", "OTP"]


def iban_gecerli(s: str) -> bool:
    s = re.sub(r"\s", "", s).upper()
    if not re.fullmatch(r"TR\d{24}", s):
        return False
    yeniden = s[4:] + s[:4]
    sayi = "".join(str(int(c, 36)) for c in yeniden)  # T→29, R→27
    return int(sayi) % 97 == 1


def luhn_gecerli(rakamlar: str) -> bool:
    toplam = 0
    for i, c in enumerate(reversed(rakamlar)):
        d = int(c)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        toplam += d
    return toplam % 10 == 0


def tckn_gecerli(s: str) -> bool:
    if not re.fullmatch(r"[1-9]\d{10}", s):
        return False
    d = [int(c) for c in s]
    tek, cift = sum(d[0:9:2]), sum(d[1:8:2])
    return (tek * 7 - cift) % 10 == d[9] and sum(d[:10]) % 10 == d[10]


@dataclass(frozen=True)
class Bulgu:
    tip: str
    bas: int
    bit: int
    metin: str
    gecerli: bool = True


def bul(metin: str, ek_araliklar: list[tuple[str, int, int]] = ()) -> list[Bulgu]:
    """Çakışmasız PII bulguları (önceliğe göre), kanonik ofsetlerle."""
    adaylar: list[Bulgu] = [Bulgu(tip, b, e, metin[b:e]) for tip, b, e in ek_araliklar]
    for m in _IBAN.finditer(metin):
        adaylar.append(Bulgu("IBAN", m.start(), m.end(), m.group(), iban_gecerli(m.group())))
    for m in _KART.finditer(metin):
        r = re.sub(r"\D", "", m.group())
        if 13 <= len(r) <= 19 and luhn_gecerli(r):
            adaylar.append(Bulgu("KART", m.start(), m.end(), m.group()))
    for m in _TCKN.finditer(metin):
        if tckn_gecerli(m.group()):
            adaylar.append(Bulgu("TCKN", m.start(), m.end(), m.group()))
    for m in _TEL.finditer(metin):
        adaylar.append(Bulgu("TEL", m.start(), m.end(), m.group()))
    for m in _EPOSTA.finditer(metin):
        adaylar.append(Bulgu("EPOSTA", m.start(), m.end(), m.group()))

    adaylar.sort(key=lambda b: (ONCELIK.index(b.tip), b.bas))
    secilen: list[Bulgu] = []
    for b in adaylar:
        if all(b.bit <= s.bas or b.bas >= s.bit for s in secilen):
            secilen.append(b)
    return sorted(secilen, key=lambda b: b.bas)


@dataclass
class Maskeli:
    metin: str
    # (tip, kanonik_bas, kanonik_bit, maske_bas, maske_bit)
    parcalar: list[tuple[str, int, int, int, int]] = field(default_factory=list)

    def kanonige(self, bas: int, bit: int) -> tuple[int, int]:
        """Maskeli metindeki bir aralığı kanonik metindeki aralığa çevirir (arayüz vurgusu için).
        Bir maske etiketinin içine düşen uç, etiketin kapsadığı orijinal parçanın ucuna genişler."""
        return self._cevir(bas, sol=True), self._cevir(bit, sol=False)

    def _cevir(self, i: int, sol: bool) -> int:
        kayma = 0
        for _, kb, kbit, mb, mbit in self.parcalar:
            if i <= mb:                      # etiketten önce (veya tam başında)
                return i + kayma
            if i < mbit:                     # etiketin içinde → orijinal parçanın ucuna genişlet
                return kb if sol else kbit
            if i == mbit:                    # etiketin hemen sonunda
                return kbit
            kayma = kbit - mbit
        return i + kayma


def maskele(metin: str, ek_araliklar: list[tuple[str, int, int]] = ()) -> Maskeli:
    parcalar, out, son, mpos = [], [], 0, 0
    for b in bul(metin, ek_araliklar):
        out.append(metin[son:b.bas])
        mpos += b.bas - son
        etiket = f"[{b.tip}]"
        parcalar.append((b.tip, b.bas, b.bit, mpos, mpos + len(etiket)))
        out.append(etiket)
        mpos += len(etiket)
        son = b.bit
    out.append(metin[son:])
    return Maskeli("".join(out), parcalar)
