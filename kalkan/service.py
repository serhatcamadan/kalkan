"""KALKAN · service.py — uçtan uca analiz hattı                          v1.2 · 2026-11-22

v1.2 (Adım 9b, kırpma saldırısı): girdi HAM_MAKS (10.000) karaktere kadar okunur. Deterministik sinyaller,
      maske, enjeksiyon taraması ve KURAL katmanı metnin tamamında; MODEL ilk GIRDI_MAKS (2.000) karakteri görür.
      Önceden ilk 2.000 karakterden sonrası hiç görülmüyordu: dolandırıcılık uzun zararsız bir metnin arkasına
      saklanabiliyordu. Kırpılan girdi "düşük" alamaz (kalkan/katman.py kural 0).

v1.1 (Adım 9a): katman=True → ürün yolu (ADR-0006): kural birinci katman + model ikinci görüş (kalkan/katman.py).
      katman=False → yalnızca model yolu (değerlendirmede modelin kendisini ölçmek için; v1 davranışı).
      hazirla() ve kural_karari() eval/katmanli.py ile paylaşılır: ölçülen = çalışan.

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
from .istem import ISTEMLER
from .katman import katmanla
from .kural import kural_ciktisi
from .normalize import Metin
from .pii import maskele
from .policy import Karar, karar_ver
from .schema import ALINTI_MAKS, KANIT_MAKS, Kanit, ModelCiktisi, SistemCevabi, Tur
from .signals import cikar, maske_araliklari

GIRDI_MAKS = 2000      # modelin gördüğü (maskeli) metin
HAM_MAKS = 10000       # okunan ham metin; ötesi atılır ve girdi_kirpildi işaretlenir


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
    onbellek_token: int = 0
    # katman=True (ürün yolu) ara durumları; katman=False'ta model kararı ve kural alanları boş kalır
    kural_tur: str | None = None
    kural_risk: str | None = None
    model_risk: str | None = None
    katman_kaynak: str | None = None


@dataclass
class Hazir:
    metin: Metin
    sinyaller: list
    maskeli: str              # metnin TAMAMI (≤ HAM_MAKS), maskeli: kural katmanı ve enjeksiyon taraması
    enjeksiyon: list[str]
    model_girdisi: str = ""   # maskeli[:GIRDI_MAKS]: model bunu görür, model kanıtları buna karşı doğrulanır
    kirpildi: bool = False    # model metnin tamamını göremedi (ya da ham HAM_MAKS'ı aştı)


def hazirla(ham: str) -> Hazir:
    """1–4: normalize → HAM metinden sinyal → PII/OTP maske → enjeksiyon taraması (modelden bağımsız, deterministik)."""
    m = Metin(ham[:HAM_MAKS])
    sinyaller = cikar(m)
    maskeli = maskele(m.kanonik, maske_araliklari(sinyaller)).metin
    kirpildi = len(ham) > HAM_MAKS or len(maskeli) > GIRDI_MAKS
    return Hazir(m, sinyaller, maskeli, tara(maskeli), maskeli[:GIRDI_MAKS], kirpildi)


def kanitlari_dogrula(kanitlar: list[dict], maskeli: str) -> tuple[list, list]:
    """Sözlük kanıtları şemaya çevirip kapıdan geçirir (bozuk öğe sessizce düşer)."""
    gecerli = []
    for k in kanitlar:
        try:
            gecerli.append(Kanit.model_validate(k))
        except ValidationError:
            pass
    return kapi(gecerli, maskeli)


def kural_karari(h: Hazir) -> tuple[Karar, Tur, list]:
    """Birinci katman: kural modeli + aynı politika."""
    c = kural_ciktisi(h.maskeli, {s.tip for s in h.sinyaller})
    tur = Tur(c["tur"])
    gecen, _ = kanitlari_dogrula(c["kanitlar"], h.maskeli)
    return karar_ver(tur, gecen, h.sinyaller, h.enjeksiyon), tur, gecen


def analiz(ham: str, arka_uc, trace_id: str | None = None, istem: str = "tam",
           katman: bool = False) -> tuple[SistemCevabi, Iz]:
    """Ürün yolu: analiz(ham, arka_uc, istem="kisa", katman=True)."""
    trace_id = trace_id or uuid.uuid4().hex[:16]
    h = hazirla(ham)
    sinyaller, maskeli, enjeksiyon = h.sinyaller, h.model_girdisi, h.enjeksiyon   # model yolu: modelin gördüğü

    tur, ham_kanitlar, json_gecerli, hata, cevap = None, [], False, None, None
    if arka_uc is None:
        hata = "arka_uc_yok"
    else:
        cevap = arka_uc.sohbet(ISTEMLER[istem](), sarmala(maskeli), ModelCiktisi.llm_json_schema())
        hata = cevap.hata or ("kesildi" if cevap.kesildi else None)
        if cevap.metin is not None:
            try:
                d = json.loads(cevap.metin)
                if isinstance(d, dict) and isinstance(d.get("kanitlar"), list):
                    # Şema sınırlarını uygulayamayan sağlayıcılar için (bazı strict modlar maxItems/maxLength
                    # desteklemez): fazlası ve 80 karakteri aşan alıntı atılır, tüm cevap çöpe gitmez.
                    d["kanitlar"] = [k for k in d["kanitlar"] if len(str((k or {}).get("alinti", ""))) <= ALINTI_MAKS][:KANIT_MAKS]
                cikti = ModelCiktisi.model_validate(d)
                tur, ham_kanitlar, json_gecerli = cikti.tur, cikti.kanitlar, True
            except (ValueError, ValidationError) as e:
                hata = ("kesildi; " if cevap.kesildi else "") + f"sema: {str(e)[:120]}"
                ham_kanitlar = _gevsek_kanitlar(cevap.metin)      # metrik için; politikaya GİRMEZ

    gecen, dusen = kapi(ham_kanitlar if json_gecerli else [], maskeli)
    k = karar_ver(tur, gecen, sinyaller, enjeksiyon)
    goster_tur, goster_kanit, ek = tur, gecen, {}
    if katman:
        kk, k_tur, k_kanit = kural_karari(h)
        kat = katmanla(kk, k_tur, k_kanit, tur, gecen, model_cevap_verdi=json_gecerli, girdi_kirpildi=h.kirpildi)
        ek = {"kural_tur": k_tur.value, "kural_risk": kk.risk.value, "model_risk": k.risk.value,
              "katman_kaynak": kat.kaynak}
        k, goster_tur, goster_kanit = kat.karar, kat.tur, kat.kanitlar
    sonuc = SistemCevabi(trace_id=trace_id, risk=k.risk, tur=goster_tur, kanitlar=goster_kanit, sinyaller=sinyaller,
                         oneri_kodu=k.oneri_kodu, mesaj=k.mesaj, dusurulen_kanit=len(dusen), girdi_kirpildi=h.kirpildi)
    iz = Iz(maskeli, ham_kanitlar, tur.value if tur else None, json_gecerli, hata,
            cevap.sure_ms if cevap else 0.0, cevap.girdi_token if cevap else 0, cevap.cikti_token if cevap else 0,
            cevap.metin if cevap else None, bool(cevap and cevap.kesildi), cevap.onbellek_token if cevap else 0, **ek)
    return sonuc, iz


def _gevsek_kanitlar(metin: str) -> list[Kanit]:
    try:
        d = json.loads(metin)
        return [Kanit.model_construct(alinti=str(k.get("alinti", "")), sinyal=k.get("sinyal")) for k in d.get("kanitlar", [])]
    except Exception:  # noqa: BLE001
        return []
