"""KALKAN · normalize.py — Türkçe metin normalleştirme               v1 · 2026-11-19

Tek kural: **bütün ofsetler `kanonik` metne göredir.** Kanonik metin, ham mesajdan bir kez
üretilir ve sonra sinyaller, PII maskeleme, kanıt kapısı ve arayüz vurgusu hep onu kullanır.

    kanonik = NFKC(ham) − görünmez karakterler (sıfır genişlikli, yön işaretleri, kontrol)

Kanonik metinden türetilen görünümler **uzunluk korur** (her karakter tek karaktere eşlenir),
böylece bir görünümde bulunan [başlangıç, bitiş) aralığı kanonik metinde de aynı yeri gösterir:

    tr_kucuk : Türkçe küçük harf (I→ı, İ→i)           "AI"   → "aı"
    kucuk    : Python str.lower (İ hariç)              "AI"   → "ai"
    ascii    : tr_kucuk + aksan katlama (ç→c, ı→i …)   "ÇIKIŞ" → "cikis"
    iskelet  : ascii + Kiril/Yunan benzer harf → Latin  "mаvibank" (Kiril а) → "mavibank"

Tuzak: Python'da "İ".lower() == "i̇" (2 karakter: i + U+0307 birleşik nokta). Düz .lower()
kullanmak ofsetleri kaydırır ve "İADE" → "i̇ade" eşleşmeyi bozar.
"""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass
from functools import cached_property

# Sıfır genişlikli ve yön kontrol karakterleri: saldırganın "ka​rgo" gibi eşleşme kırması için.
GORUNMEZ = {
    "​", "‌", "‍", "⁠", "﻿", "­",            # ZWSP, ZWNJ, ZWJ, WJ, BOM, yumuşak tire
    "‎", "‏", "‪", "‫", "‬", "‭", "‮",  # yön işaretleri / RLO
    "⁦", "⁧", "⁨", "⁩",
}

# Görsel olarak Latin harfe benzeyen Kiril/Yunan harfleri (homoglyph). Küçük harf girişi bekler.
BENZER = str.maketrans({
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c", "у": "y", "х": "x", "і": "i", "ј": "j",
    "ѕ": "s", "һ": "h", "ԁ": "d", "ӏ": "l", "ԛ": "q", "ԝ": "w", "к": "k", "м": "m", "т": "t",
    "в": "b", "н": "h",
    "α": "a", "ο": "o", "ρ": "p", "ν": "v", "τ": "t", "ι": "i", "κ": "k", "χ": "x", "υ": "u",
    "ε": "e", "μ": "u",
    "0": "o", "1": "l",  # yalnızca iskelet görünümünde; alan adı benzerliği için ("g00gle")
})

_TR_KATLA = str.maketrans({"ç": "c", "ğ": "g", "ı": "i", "ö": "o", "ş": "s", "ü": "u",
                           "â": "a", "î": "i", "û": "u"})


def kanonik(ham: str) -> str:
    """NFKC + görünmez/kontrol karakterlerini at (\\n ve \\t kalır)."""
    t = unicodedata.normalize("NFKC", ham)
    return "".join(c for c in t if c not in GORUNMEZ and (c in "\n\t" or unicodedata.category(c) != "Cc"))


def tr_kucuk(s: str) -> str:
    """Türkçe küçük harf. Uzunluk korur."""
    return s.replace("I", "ı").replace("İ", "i").lower()


def kucuk(s: str) -> str:
    """Python lower; yalnızca İ'nin 2 karaktere açılmasını engeller. Uzunluk korur."""
    return s.replace("İ", "i").lower()


def _katla_tek(c: str) -> str:
    c2 = c.translate(_TR_KATLA)
    if c2 != c:
        return c2
    d = unicodedata.normalize("NFD", c)
    taban = "".join(x for x in d if not unicodedata.combining(x))
    return taban if len(taban) == 1 else c


def asciile(s: str) -> str:
    """Karakter karakter aksan katlama. Uzunluk korur (eşlenemeyen karakter olduğu gibi kalır)."""
    return "".join(_katla_tek(c) for c in s)


@dataclass(frozen=True)
class Metin:
    """Bir mesajın kanonik hali ve uzunluk koruyan görünümleri."""

    ham: str

    @cached_property
    def kanonik(self) -> str:
        return kanonik(self.ham)

    @cached_property
    def tr_kucuk(self) -> str:
        return tr_kucuk(self.kanonik)

    @cached_property
    def kucuk(self) -> str:
        return kucuk(self.kanonik)

    @cached_property
    def ascii(self) -> str:
        return asciile(self.tr_kucuk)

    @cached_property
    def iskelet(self) -> str:
        return self.ascii.translate(BENZER)

    def __post_init__(self) -> None:  # tasarım güvencesi: görünümler hep aynı boyda
        n = len(self.kanonik)
        assert len(self.tr_kucuk) == len(self.kucuk) == len(self.ascii) == len(self.iskelet) == n
