"""KALKAN · service.py — uçtan uca analiz hattı                          v1 · 2026-11-20

  ham metin
   1 normalize    → kanonik (Metin)
   2 sinyaller    → HAM metinden (gizli karakterler dahil), maskelemeden ÖNCE  (ADR-0003, Adım 4 bulgusu)
   3 PII + OTP maske
   4 enjeksiyon taraması + güvenli sarmalama
   5 model (arka uç; yoksa veya hata verirse fail-closed)
   6 JSON şema doğrulaması (ModelCiktisi)
   7 KAPI: maskeli metinde birebir olmayan alıntı düşer
   8 politika (kod) → risk + öneri
   9 SistemCevabi + trace_id  (denetim kaydı: Adım 9)
"""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass

from pydantic import ValidationError

from .gate import kapi
from .injection import sarmala, tara
from .istem import sistem_istemi
from .normalize import Metin
from .pii import maskele
from .policy import karar_ver
from .schema import Kanit, ModelCiktisi, SistemCevabi
from .signals import cikar, maske_araliklari

GIRDI_MAKS = 2000


@dataclass
class Iz:
    """Değerlendirme için ara durumlar (kullanıcıya dönmez)."""
    model_girdisi: str
    ham_kanitlar: list[Kanit]       # KAPI ÖNCESİ (kanıt geçerliliği metriği bunu ölçer)
    tur_ham: str | None
    json_gecerli: bool
    hata: str | None
    sure_ms: float
    girdi_token: int
    cikti_token: int
    ham_cikti: str | None
    kesildi: bool = False


def analiz(ham: str, arka_uc, trace_id: str | None = None) -> tuple[SistemCevabi, Iz]:
    trace_id = trace_id or uuid.uuid4().hex[:16]
    m = Metin(ham[:GIRDI_MAKS])
    sinyaller = cikar(m)
    maskeli = maskele(m.kanonik, maske_araliklari(sinyaller)).metin
    enjeksiyon = tara(maskeli)

    tur, ham_kanitlar, json_gecerli, hata, cevap = None, [], False, None, None
    if arka_uc is None:
        hata = "arka_uc_yok"
    else:
        cevap = arka_uc.sohbet(sistem_istemi(), sarmala(maskeli), ModelCiktisi.llm_json_schema())
        hata = cevap.hata or ("kesildi" if cevap.kesildi else None)
        if cevap.metin is not None:
            try:
                cikti = ModelCiktisi.model_validate(json.loads(cevap.metin))
                tur, ham_kanitlar, json_gecerli = cikti.tur, cikti.kanitlar, True
            except (ValueError, ValidationError) as e:
                hata = ("kesildi; " if cevap.kesildi else "") + f"sema: {str(e)[:120]}"
                ham_kanitlar = _gevsek_kanitlar(cevap.metin)      # metrik için; politikaya GİRMEZ

    gecen, dusen = kapi(ham_kanitlar if json_gecerli else [], maskeli)
    k = karar_ver(tur, gecen, sinyaller, enjeksiyon)
    sonuc = SistemCevabi(trace_id=trace_id, risk=k.risk, tur=tur, kanitlar=gecen, sinyaller=sinyaller,
                         oneri_kodu=k.oneri_kodu, mesaj=k.mesaj, dusurulen_kanit=len(dusen))
    iz = Iz(maskeli, ham_kanitlar, tur.value if tur else None, json_gecerli, hata,
            cevap.sure_ms if cevap else 0.0, cevap.girdi_token if cevap else 0, cevap.cikti_token if cevap else 0,
            cevap.metin if cevap else None, bool(cevap and cevap.kesildi))
    return sonuc, iz


def _gevsek_kanitlar(metin: str) -> list[Kanit]:
    try:
        d = json.loads(metin)
        return [Kanit.model_construct(alinti=str(k.get("alinti", "")), sinyal=k.get("sinyal")) for k in d.get("kanitlar", [])]
    except Exception:  # noqa: BLE001
        return []
