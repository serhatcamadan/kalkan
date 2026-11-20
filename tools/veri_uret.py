"""KALKAN · Adım 3 · sentetik veri üretici                            v1 · 2026-11-20
🧪 KESİN DENE:  python tools/veri_uret.py          (tohum sabit → aynı çıktı)

Girdi : data/templates/sablonlar.yaml, data/adversarial/adversarial.yaml
Çıktı : data/splits/{egitim,dogrulama,test}.jsonl, data/adversarial/adversarial.jsonl, data/splits/uretim_raporu.json

Her satır:
  id, sablon_id, split, tur, marka, gurultu[], metin (HAM, kanonik değil),
  model_girdisi (kanonik + PII/OTP maskeli → modelin göreceği tek şey),
  hedef (ModelCiktisi: kanıt alıntıları MASKELİ metinde birebir, kompakt JSON için hazır)

Kurallar
  • Bölme ŞABLON bazında (sablonlar.yaml → split) ve marka havuzu bölüme özel → ezber/sızıntı ölçülebilir.
  • Kanıt alıntısı işaretlerle (⟦sinyal:…⟧) üretilir, gürültü işaretlere dokunmaz → alıntı daima birebir.
  • Doğrulanamayan örnek (maskeli alıntı maskeli metinde yok, şema hatası) SESSİZCE değil, sayılarak düşürülür.
  • Telefonlar 0599/0850 999 aralığından, IBAN'lar banka kodu 99999 ile üretilir (tahsisli olmaması amaçlanmıştır).
"""
from __future__ import annotations

import argparse
import json
import random
import re
import string
import sys
from collections import Counter
from pathlib import Path

import yaml

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))

from kalkan.normalize import Metin, asciile  # noqa: E402
from kalkan.pii import iban_gecerli, luhn_gecerli, maskele  # noqa: E402
from kalkan.schema import ALINTI_MAKS, ModelCiktisi, Sinyal  # noqa: E402
from kalkan.signals import cikar, maske_araliklari  # noqa: E402

HEDEF_SAYI = {"egitim": 1500, "dogrulama": 200, "test": 300}
TOHUM = 20261120
ISARET = re.compile(r"⟦([a-z_]+):(.*?)⟧", re.S)
SPIN = re.compile(r"\{([^{}]*\|[^{}]*)\}")
SLOT = re.compile(r"\{([A-Z_]+)\}")
ISARET_KAR = {"⟦", "⟧", ":"}

ADLAR = ["Ahmet", "Ayşe", "Mehmet", "Fatma", "Emre", "Zeynep", "Burak", "Elif", "Can", "Selin", "Murat", "Deniz",
         "Hakan", "Esra", "Oğuz", "Gül", "İsmail", "Şule", "Ümit", "Çağla"]
YAKINLAR = ["Anne", "Baba", "Abla", "Abi", "Kanka", "Teyze", "Dayı", "Annecim", "Babacım", "Kardeşim"]
SURELER = ["24 saat", "2 saat", "48 saat", "30 dakika", "1 saat", "12 saat", "3 gün"]


def slug(marka: str) -> str:
    return re.sub(r"[^a-z0-9]", "", asciile(marka.replace("I", "ı").replace("İ", "i").lower()))


# ───────────────────────────────────────── slot üreticileri
def tutar(r: random.Random, lo: int, hi: int, kurus: bool) -> str:
    v = r.randint(lo, hi)
    s = f"{v:,}".replace(",", ".")
    if kurus:
        s += "," + r.choice(["90", "99", "50", "00", "49"])
    return s + r.choice([" TL", " TL", " TL", "₺", " lira"]) if not s.startswith("₺") else s


def iban(r: random.Random) -> str:
    govde = "99999" + "0" + "".join(r.choice(string.digits) for _ in range(16))
    for kk in range(100):
        a = f"TR{kk:02d}{govde}"
        if iban_gecerli(a):
            return a if r.random() < 0.4 else " ".join(a[i:i + 4] for i in range(0, 26, 4))
    raise RuntimeError


def tel(r: random.Random) -> str:
    n = f"0599 {r.randint(100, 999)} {r.randint(10, 99)} {r.randint(10, 99)}"
    return r.choice([n, n.replace(" ", ""), "+90 " + n[1:]])


def sahte_link(r: random.Random, s: str, tax: dict) -> str:
    tld = r.choice(tax["supheli_tld"] + ["com", "net", "info"])
    sablon = r.choice(["{s}-guvenlik", "{s}-destek", "{s}online", "{s}-tr", "{s}-iade", "e{s}", "{s}giris", "{t}"])
    t = list(s)
    if len(t) > 4:  # harf yer değiştirme (typosquat)
        i = r.randint(1, len(t) - 3)
        t[i], t[i + 1] = t[i + 1], t[i]
    host = f"{sablon.format(s=s, t=''.join(t))}.{tld}"
    yol = r.choice(["", "/giris", "/odeme", "/dogrula", f"/{r.randint(1000, 9999)}", "/tr/islem"])
    link = r.choice(["https://", "http://", "", "www."]) + host + yol
    if r.random() < 0.08:  # güvenlik raporundan iletilmiş gibi: defang
        link = link.replace("http", "hxxp").replace(".", "[.]", 1)
    return link


def kisa_link(r: random.Random, tax: dict) -> str:
    alan = r.choice(tax["kisa_link_alanlari"][:9])
    return f"{r.choice(['https://', ''])}{alan}/{''.join(r.choice(string.ascii_letters + string.digits) for _ in range(r.randint(5, 8)))}"


def slot_doldur(ad: str, r: random.Random, bag: dict, tax: dict) -> str:
    havuz, marka = bag["havuz"], bag["marka"]
    s = slug(marka)
    if ad == "MARKA":
        return marka
    if ad == "ETICARET":
        return r.choice(havuz["eticaret"])
    if ad == "LINK":
        return sahte_link(r, s, tax)
    if ad == "RESMI_LINK":
        return r.choice(["https://", "", "www."]) + f"{s}.com.tr" + r.choice(["", "/kampanya", "/takip", "/fatura"])
    if ad == "KISA_LINK":
        return kisa_link(r, tax)
    if ad == "BAHIS_LINK":
        return f"{r.choice(['https://', ''])}{s}{r.randint(100, 999)}.{r.choice(['com', 'net', 'xyz', 'top', 'vip', 'win'])}"
    if ad == "GRUP_LINK":
        kod = "".join(r.choice(string.ascii_letters + string.digits) for _ in range(10))
        return r.choice([f"t.me/+{kod}", f"https://t.me/{s}vip", f"chat.whatsapp.com/{kod}"])
    if ad == "TUTAR_K":
        return tutar(r, 19, 149, True)
    if ad == "TUTAR_O":
        return tutar(r, 250, 4999, r.random() < 0.3)
    if ad == "TUTAR_B":
        return tutar(r, 5000, 95000, False)
    if ad == "SURE":
        return r.choice(SURELER)
    if ad == "IBAN":
        return iban(r)
    if ad == "TEL":
        return tel(r)
    if ad == "OTP":
        return str(r.randint(10 ** 5, 10 ** 6 - 1)) if r.random() < 0.7 else str(r.randint(1000, 9999))
    if ad == "TAKIP":
        return r.choice(["HK", "KG", "TK", "SP"]) + str(r.randint(10 ** 8, 10 ** 9 - 1))
    if ad == "YAKIN":
        return r.choice(YAKINLAR)
    if ad == "AD":
        return r.choice(ADLAR)
    if ad == "YUZDE":
        return str(r.choice([20, 25, 30, 40, 50, 70, 120, 200, 340, 500]))
    if ad == "TARIH":
        return f"{r.randint(1, 28):02d}.{r.randint(1, 12):02d}.2026"
    if ad == "SAAT":
        return f"{r.randint(8, 22):02d}:{r.choice(['00', '15', '30', '45'])}"
    if ad == "KISA_NO":
        return r.choice(["3434", "4848", "7000", "2525"])
    if ad == "MERSIS":
        while True:
            m = "0" + "".join(r.choice(string.digits) for _ in range(15))
            if not luhn_gecerli(m):
                return m
    raise KeyError(f"Bilinmeyen slot: {ad}")


# ───────────────────────────────────────── gürültü (işaret karakterlerine dokunmaz)
def _isaret_disi(metin: str, f) -> str:
    """f'i yalnızca ⟦sinyal: önekleri ve ⟧ dışındaki karakterlere uygular."""
    parcalar = re.split(r"(⟦[a-z_]+:|⟧)", metin)
    return "".join(p if re.fullmatch(r"⟦[a-z_]+:|⟧", p) else f(p) for p in parcalar)


def yazim_hatasi(r: random.Random):
    """Yalnızca TAMAMEN harften oluşan ≥5 harfli kelimelere dokunur: link, sayı, kod, IBAN bozulmaz."""
    def f(p: str) -> str:
        kelimeler = [m for m in re.finditer(r"(?<![\w./:@+-])[^\W\d_]{5,}(?![\w./:@+-])", p)]
        if not kelimeler or r.random() < 0.5:
            return p
        m = r.choice(kelimeler)
        w = m.group()
        i = r.randint(1, len(w) - 2)
        islem = r.choice(["sil", "cift", "takas"])
        w2 = {"sil": w[:i] + w[i + 1:], "cift": w[:i] + w[i] + w[i:],
              "takas": w[:i] + w[i + 1] + w[i] + w[i + 2:]}[islem]
        return p[:m.start()] + w2 + p[m.end():]
    return f


def gurultu_uygula(metin: str, r: random.Random) -> tuple[str, list[str]]:
    etiketler = []
    if r.random() < 0.25:
        metin = _isaret_disi(metin, lambda p: asciile(p).replace("İ", "I"))
        etiketler.append("ascii")
    if r.random() < 0.08:
        metin = _isaret_disi(metin, lambda p: p.replace("i", "İ").replace("ı", "I").upper())
        etiketler.append("buyuk_harf")
    if r.random() < 0.15:
        metin = _isaret_disi(metin, yazim_hatasi(r))
        etiketler.append("yazim")
    if r.random() < 0.10:
        metin = _isaret_disi(metin, lambda p: re.sub(r" ", lambda _: " " * r.choice([1, 1, 2]), p))
        etiketler.append("bosluk")
    if r.random() < 0.08:
        metin = r.choice(["⚠️ ", "📦 ", "🎁 ", "‼️ ", "🔔 "]) + metin
        etiketler.append("emoji")
    return metin, etiketler


# ───────────────────────────────────────── tek örnek
def isle(isaretli: str) -> tuple[str, list[tuple[str, str]]]:
    kanitlar = [(m.group(1), m.group(2)) for m in ISARET.finditer(isaretli)]
    return ISARET.sub(lambda m: m.group(2), isaretli), kanitlar


def kirp(alinti: str) -> str:
    if len(alinti) <= ALINTI_MAKS:
        return alinti
    k = alinti[:ALINTI_MAKS]
    return k[: k.rfind(" ")] if " " in k else k


def ornek_uret(sablon: dict, split: str, r: random.Random, tax: dict, havuzlar: dict) -> dict:
    havuz = havuzlar[split]
    bag = {"havuz": havuz, "marka": r.choice(havuz[sablon["marka"]])}
    t = sablon["metin"]
    while SPIN.search(t):
        t = SPIN.sub(lambda m: r.choice(m.group(1).split("|")), t)
    t = SLOT.sub(lambda m: slot_doldur(m.group(1), r, bag, tax), t)
    t, gurultu = gurultu_uygula(t, r)
    metin, kanit_ham = isle(t)

    m = Metin(metin)
    maskeli = maskele(m.kanonik, maske_araliklari(cikar(m, tax)))
    kanitlar = []
    for sinyal, alinti in kanit_ham:
        alinti_k = Metin(alinti).kanonik
        alinti_m = kirp(maskele(alinti_k, maske_araliklari(cikar(Metin(alinti_k), tax))).metin.strip())
        if alinti_m not in maskeli.metin:
            raise ValueError(f"alıntı maskeli metinde yok: {alinti_m!r}")
        kanitlar.append({"alinti": alinti_m, "sinyal": sinyal})
    hedef = ModelCiktisi.model_validate({"kanitlar": kanitlar, "tur": sablon["tur"]})
    return {"sablon_id": sablon["id"], "split": split, "tur": sablon["tur"], "marka": bag["marka"],
            "gurultu": gurultu, "metin": metin, "model_girdisi": maskeli.metin,
            "hedef": hedef.model_dump(mode="json")}


def adversarial_uret(tax: dict) -> list[dict]:
    kaynak = yaml.safe_load(open(KOK / "data/adversarial/adversarial.yaml", encoding="utf-8"))
    out = []
    for a in kaynak["ornekler"]:
        m = Metin(a["metin"])
        out.append({**a, "split": "adversarial",
                    "model_girdisi": maskele(m.kanonik, maske_araliklari(cikar(m, tax))).metin})
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tohum", type=int, default=TOHUM)
    a = ap.parse_args()
    from kalkan.taxonomy import yukle
    tax = yukle()
    kaynak = yaml.safe_load(open(KOK / "data/templates/sablonlar.yaml", encoding="utf-8"))
    sablonlar, havuzlar = kaynak["sablonlar"], kaynak["havuzlar"]
    gecerli_sinyal = {s.value for s in Sinyal}
    for s in sablonlar:  # şablon sözdizimi denetimi
        isaretler = ISARET.findall(s["metin"])
        assert len(isaretler) <= 3, f"{s['id']}: 3'ten fazla kanıt işareti"
        assert all(x[0] in gecerli_sinyal for x in isaretler), f"{s['id']}: geçersiz sinyal"

    rapor = {"tohum": a.tohum, "dusurulen": Counter(), "uretilen": {}}
    out_dir = KOK / "data/splits"
    out_dir.mkdir(parents=True, exist_ok=True)
    for split, hedef_n in HEDEF_SAYI.items():
        r = random.Random(f"{a.tohum}-{split}")
        grup = [s for s in sablonlar if s["split"] == split]
        turler = sorted({s["tur"] for s in grup})
        tur_basi = hedef_n // len(turler)
        satirlar, gorulen = [], set()
        for tur in turler:
            tsab = [s for s in grup if s["tur"] == tur]
            n, deneme = 0, 0
            while n < tur_basi and deneme < tur_basi * 20:
                deneme += 1
                s = tsab[n % len(tsab)]
                try:
                    o = ornek_uret(s, split, r, tax, havuzlar)
                except Exception as e:  # noqa: BLE001
                    rapor["dusurulen"][f"{s['id']}: {type(e).__name__}: {str(e)[:60]}"] += 1
                    continue
                if o["metin"] in gorulen:
                    rapor["dusurulen"]["tekrar"] += 1
                    continue
                gorulen.add(o["metin"])
                o["id"] = f"{split[:3]}-{len(satirlar):05d}"
                satirlar.append(o)
                n += 1
        r.shuffle(satirlar)
        with open(out_dir / f"{split}.jsonl", "w", encoding="utf-8") as f:
            for o in satirlar:
                f.write(json.dumps(o, ensure_ascii=False) + "\n")
        rapor["uretilen"][split] = len(satirlar)
        print(f"{split:10s} {len(satirlar):5d} örnek · {len(grup)} şablon · {len(turler)} tür")

    adv = adversarial_uret(tax)
    with open(KOK / "data/adversarial/adversarial.jsonl", "w", encoding="utf-8") as f:
        for o in adv:
            f.write(json.dumps(o, ensure_ascii=False) + "\n")
    print(f"adversarial {len(adv):4d} örnek")
    rapor["uretilen"]["adversarial"] = len(adv)
    rapor["dusurulen"] = dict(rapor["dusurulen"])
    (out_dir / "uretim_raporu.json").write_text(json.dumps(rapor, ensure_ascii=False, indent=1))
    print("düşürülen:", sum(rapor["dusurulen"].values()), "→ data/splits/uretim_raporu.json")


if __name__ == "__main__":
    main()
