"""KALKAN · schema.py — model çıktısı ve sistem cevabı şemaları        v1 · 2026-11-19

İki ayrı sözleşme var:

1. `ModelCiktisi`: modelin ürettiği TEK şey. Önce kanıt, sonra tür. Risk YOK.
   Adım 1 dersi (VPS'te gecikmeyi üretilen token sayısı belirliyor) yüzünden kompakt:
   en fazla 3 kanıt, alıntı en fazla 80 karakter, girintisiz JSON.
2. `SistemCevabi`: kodun kullanıcıya döndürdüğü şey. Risk ve öneri kodu POLİTİKA KODUNDAN gelir.
   "güvenli" ve benzeri ifadeler yasak (ADR-0004); en iyi durumda "belirgin işaret bulunamadı".
"""
from __future__ import annotations

import json
import re
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

from .normalize import asciile, tr_kucuk


class Tur(str, Enum):
    sahte_kargo_gumruk = "sahte_kargo_gumruk"
    kurum_taklidi = "kurum_taklidi"
    sahte_kamu_gorevlisi = "sahte_kamu_gorevlisi"
    yatirim_vip_grup = "yatirim_vip_grup"
    yasa_disi_bahis = "yasa_disi_bahis"
    oyun_hesap_skin = "oyun_hesap_skin"
    odul_kampanya = "odul_kampanya"
    yakin_taklidi = "yakin_taklidi"
    gorev_is_ilani = "gorev_is_ilani"
    reklam_spam = "reklam_spam"
    mesru_islem = "mesru_islem"


DOLANDIRICILIK_DISI = {Tur.reklam_spam, Tur.mesru_islem}


class Sinyal(str, Enum):
    odeme_talebi = "odeme_talebi"
    kod_talebi = "kod_talebi"
    kimlik_talebi = "kimlik_talebi"
    aciliyet = "aciliyet"
    kurum_taklidi = "kurum_taklidi"
    yetki_iddiasi = "yetki_iddiasi"
    odul_vaadi = "odul_vaadi"
    gizlilik_baskisi = "gizlilik_baskisi"
    kanal_degistirme = "kanal_degistirme"
    yakinlik_iddiasi = "yakinlik_iddiasi"
    link = "link"


class Risk(str, Enum):
    yuksek = "yuksek"
    orta = "orta"
    dusuk = "dusuk"
    belirsiz = "belirsiz"  # fail-closed: şema bozuk, zaman aşımı, kapı her şeyi düşürdü…


ALINTI_MAKS = 80
KANIT_MAKS = 3
Alinti = Annotated[str, StringConstraints(strip_whitespace=False, min_length=2, max_length=ALINTI_MAKS)]


class Kanit(BaseModel):
    model_config = ConfigDict(extra="forbid")
    alinti: Alinti
    sinyal: Sinyal


class ModelCiktisi(BaseModel):
    """Modelin ürettiği JSON. Alan sırası önemli: kanıt ÖNCE (model önce kanıtı yazsın, sonra türe karar versin)."""

    model_config = ConfigDict(extra="forbid")
    kanitlar: list[Kanit] = Field(default_factory=list, max_length=KANIT_MAKS)
    tur: Tur

    def kompakt_json(self) -> str:
        """Eğitim verisinde hedef çıktı biçimi: boşluksuz, ASCII kaçışsız."""
        return json.dumps(self.model_dump(mode="json"), ensure_ascii=False, separators=(",", ":"))

    @classmethod
    def llm_json_schema(cls) -> dict:
        """llama-server / OpenAI `response_format` için şema. Her nesnede tüm alanlar `required`
        (OpenAI strict modu bunu ister; llama-server gramerinde de kanitlar alanı atlanamaz)."""
        sch = cls.model_json_schema()

        def zorunlu(d):
            if isinstance(d, dict):
                if d.get("type") == "object" and "properties" in d:
                    d["required"] = list(d["properties"])
                    d["additionalProperties"] = False
                    for p in d["properties"].values():
                        p.pop("default", None)
                for v in d.values():
                    zorunlu(v)
            elif isinstance(d, list):
                for v in d:
                    zorunlu(v)
        zorunlu(sch)
        return sch


# --------------------------------------------------------------------- sistem cevabı
_YASAK = re.compile(r"\b(guvenli\w*|guvende|zararsiz\w*|sorun\s+yok|endise\s+etmeyin\w*|tehlikesiz\w*)\b")


def yasak_ifade_var(metin: str) -> str | None:
    """Kullanıcıya giden metinde 'güvenli' ailesinden bir ifade varsa onu döndürür.
    Not: 'güvenlik' de yakalanır; kullanıcı metninde bu kelimeyi bilerek kullanmıyoruz."""
    m = _YASAK.search(asciile(tr_kucuk(metin)))
    return m.group(0) if m else None


class DeterministikSinyal(BaseModel):
    tip: str            # kisa_link, benzer_alan_adi, iban, tutar, otp, punycode, …
    deger: str          # maskeli değer veya etiket (ham PII asla buraya yazılmaz)
    bas: int            # kanonik metindeki aralık
    bit: int
    ek: dict = Field(default_factory=dict)


class DogrulanmisKanit(Kanit):
    bas: int            # maskeli metindeki aralık (kapıdan geçti)
    bit: int


class SistemCevabi(BaseModel):
    model_config = ConfigDict(extra="forbid")
    trace_id: str
    risk: Risk
    tur: Tur | None
    kanitlar: list[DogrulanmisKanit] = Field(default_factory=list)
    sinyaller: list[DeterministikSinyal] = Field(default_factory=list)
    oneri_kodu: str
    mesaj: str
    dusurulen_kanit: int = 0          # kapıdan geçemeyen alıntı sayısı (şeffaflık)
    girdi_kirpildi: bool = False      # model metnin tamamını göremedi (Adım 9b)

    @field_validator("mesaj")
    @classmethod
    def _guvenli_deme(cls, v: str) -> str:
        if (ifade := yasak_ifade_var(v)) is not None:
            raise ValueError(f"Kullanıcı mesajında yasak ifade: {ifade!r} (ADR-0004)")
        return v
