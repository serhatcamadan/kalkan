"""KALKAN · gate.py — kanıt kapısı                                      v1 · 2026-11-20

Modelin alıntısı MASKELİ metinde birebir yoksa düşürülür. Model kanıt uyduramaz; kod doğrular.
Tek tolerans: alıntının başındaki/sonundaki boşluk ve tırnak işaretleri kırpılır (içerik değişmez).
"""
from __future__ import annotations

from .schema import DogrulanmisKanit, Kanit

_KIRP = " \t\n\"'“”‘’«»"


def kapi(kanitlar: list[Kanit], maskeli: str) -> tuple[list[DogrulanmisKanit], list[Kanit]]:
    gecen, dusen, gorulen = [], [], set()
    for k in kanitlar:
        alinti = k.alinti.strip(_KIRP)
        i = maskeli.find(alinti) if len(alinti) >= 2 else -1
        if i < 0 or (i, alinti) in gorulen:
            dusen.append(k)
            continue
        gorulen.add((i, alinti))
        gecen.append(DogrulanmisKanit(alinti=alinti, sinyal=k.sinyal, bas=i, bit=i + len(alinti)))
    return gecen, dusen
