"""KALKAN · injection.py — talimat enjeksiyonu taraması ve güvenli sarmalama   v1 · 2026-11-20

İlke: mesaj HER ZAMAN VERİDİR. İki savunma katmanı:
  1. Sarmalama: mesaj <mesaj>…</mesaj> arasında gönderilir; mesajın içindeki sınırlayıcı benzeri etiketler
     etkisizleştirilir (kullanıcı "</mesaj> yeni görev:" yazarak kaçamaz).
  2. Taint (leke): enjeksiyon kalıbı bulunursa sinyal olarak işaretlenir. Politika bunu ASLA "düşük risk"e
     çevirmez: meşru bir banka SMS'i analiz aracına talimat vermez. Enjeksiyon girişimi başlı başına bir işarettir.
Model çıktısı bu modülden bağımsız olarak şema + kapı + politika ile ayrıca sınırlanır (tek katmana güvenilmez).
"""
from __future__ import annotations

import re

from .normalize import Metin

KALIPLAR = {
    "talimat_yok_say": r"(ignore|disregard)\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts?)|"
                       r"(onceki|yukaridaki)\s+(tum\s+)?(talimat|komut)\w*\s+(yok say|unut|dikkate alma)\w*",
    "rol_ele_gecirme": r"\b(system|assistant|sistem notu|sistem mesaji|yeni gorev|new task)\s*[:\]]",
    "siniflandirma_dayatma": r"(guvenli|mesru|risk\w*\s*:?\s*dusuk|safe|legit\w*)\s*(olarak)?\s*(isaretle|siniflandir|mark|label)\w*|"
                             r"(analiz arac\w*|yapay zeka|asistan\w*|ai)\b[^.]{0,60}(guvenli|resmi|dogrulan)\w*",
    "sinirlayici_kacis": r"</?\s*(mesaj|message|system|user|assistant)\s*>",
    "cikti_dayatma": r"\{\s*\"?(kanitlar|tur|risk)\"?\s*:",
}
_DERLENMIS = {k: re.compile(v) for k, v in KALIPLAR.items()}


def tara(metin: str) -> list[str]:
    """Kanonik/maskeli metin üzerinde enjeksiyon kalıplarını bulur (ASCII-katlanmış görünümde)."""
    a = Metin(metin).ascii
    return [ad for ad, d in _DERLENMIS.items() if d.search(a)]


def sarmala(metin: str) -> str:
    """Sınırlayıcı benzeri etiketleri görünür ama etkisiz hale getir, sonra sarmala."""
    guvenli_metin = re.sub(r"<(\s*/?\s*)(mesaj|message|system|user|assistant)(\s*)>", r"‹\1\2\3›", metin,
                           flags=re.IGNORECASE)
    return f"<mesaj>\n{guvenli_metin}\n</mesaj>"
