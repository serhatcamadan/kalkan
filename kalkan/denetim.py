"""KALKAN · denetim.py — metinsiz denetim kaydı (Adım 9b)                v1 · 2026-11-22

Her analiz için tek JSON satırı: NE karar verildiğini ve NEDEN (hangi katman, hangi sinyal türleri) gösterir;
mesajın kendisini, alıntıları, model ham çıktısını ve hata gövdelerini ASLA içermez (olay 2026-11-22 dersi:
mesajdan türetilmiş her metin, metindir).

  metin_ozeti: HMAC-SHA256(tuz, ham)[:16]. Aynı mesaj aynı özeti verir (tekrar eden saldırıyı görmek için),
               ama kısa SMS'ler sözlükle geri çözülemez: tuz olmadan özet hesaplanamaz.
               Tuz: KALKAN_DENETIM_TUZ ortam değişkeni. Yoksa süreç başına rastgele (özetler süreçler arasında
               eşleşmez; bilinçli olarak güvenli taraf).
  hata_turu  : yalnızca kategori ("baglanti", "zaman_asimi", "http_4xx", "sema", "kesildi", "arka_uc_yok"),
               hata METNİ değil (şema hatası model çıktısından parça taşıyabilir).
Dosya 0600 izniyle oluşturulur; satır ekleme (append-only).
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path

from . import __version__
from .katman import KATMAN_SURUMU
from .policy import POLITIKA_SURUMU

_TUZ = (os.environ.get("KALKAN_DENETIM_TUZ") or secrets.token_hex(16)).encode()


def ozet(ham: str) -> str:
    return hmac.new(_TUZ, ham.encode("utf-8"), hashlib.sha256).hexdigest()[:16]


def hata_turu(hata: str | None) -> str | None:
    if not hata:
        return None
    h = hata.lower()
    for anahtar, tur in (("arka_uc_yok", "arka_uc_yok"), ("kesildi", "kesildi"), ("sema", "sema"),
                         ("timeout", "zaman_asimi"), ("timed out", "zaman_asimi")):
        if anahtar in h:
            return tur
    if h.startswith("http 4"):
        return "http_4xx"
    if h.startswith("http 5"):
        return "http_5xx"
    return "baglanti"


def kayit(ham: str, sonuc, iz) -> dict:
    """SistemCevabi + Iz → metinsiz denetim satırı."""
    return {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "trace_id": sonuc.trace_id,
        "surum": {"kalkan": __version__, "politika": POLITIKA_SURUMU, "katman": KATMAN_SURUMU},
        "risk": sonuc.risk.value,
        "tur": sonuc.tur.value if sonuc.tur else None,
        "oneri_kodu": sonuc.oneri_kodu,
        "katman_kaynak": iz.katman_kaynak,
        "kural_risk": iz.kural_risk,
        "model_risk": iz.model_risk,
        "sinyal_tipleri": sorted({s.tip for s in sonuc.sinyaller}),
        "kanit_sinyalleri": [k.sinyal.value for k in sonuc.kanitlar],
        "dusurulen_kanit": sonuc.dusurulen_kanit,
        "girdi_uzunluk": len(ham),
        "girdi_kirpildi": sonuc.girdi_kirpildi,
        "metin_ozeti": ozet(ham),
        "hata_turu": hata_turu(iz.hata),
        "sure_ms": round(iz.sure_ms),
    }


class Denetci:
    """JSONL'e ekler. Örn. Denetci("logs/denetim.jsonl").yaz(ham, sonuc, iz)"""

    def __init__(self, yol: str | Path):
        self.yol = Path(yol)
        self.yol.parent.mkdir(parents=True, exist_ok=True)
        if not self.yol.exists():
            fd = os.open(self.yol, os.O_CREAT | os.O_WRONLY | os.O_APPEND, 0o600)
            os.close(fd)

    def yaz(self, ham: str, sonuc, iz) -> dict:
        satir = kayit(ham, sonuc, iz)
        with open(self.yol, "a", encoding="utf-8") as f:
            f.write(json.dumps(satir, ensure_ascii=False) + "\n")
        return satir
