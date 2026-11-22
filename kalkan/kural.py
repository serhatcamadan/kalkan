"""KALKAN · kural.py — kural tabanlı birinci katman (ADR-0006)            v1.3 · 2026-11-22

v1.3: eval/modeller/kural.py'den pakete taşındı: ürün (kalkan.service, katman=True) ve değerlendirme AYNI kodu
      çalıştırır ("ölçülen = çalışan"). Davranış v1.2 ile birebir aynı (tests/test_katman.py).
v1.2: deterministik sinyaller HAM metinden. v1.1: yalnızca DOĞRULAMA hatalarına bakılarak ayarlandı.

Anahtar kelime sözlükleri taksonomideki ipuçlarından ve alan bilgisinden yazıldı; golden'a göre AYARLANMADI.
Kanıt: eşleşen anahtar kelimenin geçtiği cümle parçası (≤ 80 karakter) → daima girdide birebir.
Bilinen yanlılık: şablonları ve kuralları aynı kişi (Claude) yazdı (doğrulama 0.990 → yeni şablonlarda 0.722).
"""
from __future__ import annotations

import re

from .normalize import Metin
from .schema import ALINTI_MAKS
from .signals import cikar

S = {  # sinyal → ascii-katlanmış küçük harf regex
    "yetki_iddiasi": r"savcilig\w*|savcilik\w*|bassavcilig\w*|emniyet|jandarma|masak|\bpolis\w*|komiser|sorusturma\w*|yakalama karari|giyabinizda",
    "yakinlik_iddiasi": r"\b(anne\w*|baba\w*|abla|abi|kanka|teyze|dayi|kardesim)\b|yeni numara\w*|numaram degisti|telefonum (bozuldu|caldi|suya)",
    "kod_talebi": r"(kod\w*)[^.!?]{0,40}(ilet\w*|okuy\w*|soyle\w*|yaz\w*|\bat\b|gonder\w*)|(okuyun|soyleyin|atar\w*)[^.!?]{0,30}kod\w*|guard kodu|kod\w*[^.!?]{0,30}atar\w*",
    "kimlik_talebi": r"sifre\w*|tc kimlik|kimlik bilgi\w*|kart bilgi\w*|\bcvv\b|giris yap\w*|bilgilerinizi (guncelle|dogrula|gir)\w*|dogrulay\w*|hesabinla|hesap bilgi\w*",
    "odeme_talebi": r"odey\w*|\bode\b|odeme\w* (yap|gerek)\w*|ucret(?!siz)\w*|bedel\w*|yatir\w*|gonder(ebilir|ir) mi\w*|atar misin|\bat\b|havale|komisyon|teminat|vergi|harc\w*|aktar\w*",
    "aciliyet": r"\d+\s*(saat|dakika|gun)\s*(icinde|sonra|gecerli)|\bhemen\b|\bacil\w*|son gun|son uyari|aksi halde|iptal edilecek\w*|kapatilacak\w*|silin(ecek|ir)\w*|sifirlanir|iade edilecek|imha|bugun (son|odemezseniz)",
    "kurum_taklidi": r"hesabiniz\w*[^.!?]{0,30}(askiya|bloke|kapat|dondur)\w*|mobil subeniz|olagandisi giris|supheli islem\w*|kartinizdan [^.!?]{0,30}islem",
    "odul_vaadi": r"kazan\w*|tebrikler|hediye\w*|bonus\w*|freespin|cekilis\w*|garanti\w*|kar birik\w*|getiri\w*|pasif gelir|bedava|ucretsiz|sansli|kazanc\w*",
    "gizlilik_baskisi": r"kimseye (soyle|anlat|bahset)\w*|aramizda kalsin|\w*(soyleme|anlatma)(yin)?\b|bankaya gitmeyin|bilgi vermeyin",
    "kanal_degistirme": r"whatsapp|telegram|t\.me/|discord|chat\.whatsapp|numarasini arayin|numaraya yazin|hattini arayin",
}
KONU = {  # tür → konu sözlüğü
    "yasa_disi_bahis": r"bahis|bonus|casino|slot|freespin|kupon|\bmac\b|skor|sike|giris adresi|yeni adres|domain|cevrim",
    "oyun_hesap_skin": r"skin|envanter|\boyun\w*|elmas|trade|guard|discord|turnuva|yasaklan\w*|cuzdan bakiye",
    "yatirim_vip_grup": r"borsa|kripto|yatirim|hisse|sinyal grub|portfoy|altin|doviz|kar birik|getiri|robot|aracı kurum|araci kurum",
    "gorev_is_ilani": r"is basvuru|gorev\w*|evden calis|ek gelir|ozgecmis|begen\w*|yorum gorevli|veri girisi|video basi|is ilani",
    "sahte_kargo_gumruk": r"kargo|gonderi\w*|paket\w*|koli|gumruk|kurye|teslim|dagitim|depo",
    "odul_kampanya": r"tebrikler|kazandiniz|cekilis\w*|hediye|puan\w*|sansli|anket|iade edilecek|kredi\w* tanimlandi|tanimlandi",
}
REKLAM = r"\bret\b|iptal yazip|\biys\b|mersis|kampanya|indirim|firsat|iptal edebilirsiniz|ile iptal|iletisim izni"
SUPHELI_LINK = {"marka_iceren_yabanci", "benzer_alan_adi", "kisa_link", "supheli_tld", "punycode", "unicode_alan_adi",
                "gizli_karakter"}
AYRAC = re.compile(r"[.!?;\n]|,\s")


def _parca(g: str, s: int, e: int) -> str:
    """Eşleşmenin içinde geçtiği cümle parçası; ≤ ALINTI_MAKS, daima g'nin alt dizesi."""
    bas = max((m.end() for m in AYRAC.finditer(g, 0, s)), default=0)
    son = next((m.start() for m in AYRAC.finditer(g, e)), len(g))
    while bas < s and g[bas] == " ":
        bas += 1
    if son - bas > ALINTI_MAKS:  # eşleşmeyi ortalayarak kırp
        orta = (s + e) // 2
        bas = max(bas, min(s, orta - ALINTI_MAKS // 2))
        son = min(son, bas + ALINTI_MAKS)
    return g[bas:son].strip()


def kural_ciktisi(girdi: str, tipler: set[str]) -> dict:
    """girdi: modelin göreceği maskeli metin (alıntılar buradan); tipler: HAM metnin deterministik sinyal tipleri.
    Dönüş: {"tur": str, "kanitlar": [{"alinti", "sinyal"}]}, model çıktısıyla aynı biçim."""
    g = girdi
    m = Metin(g)
    a = m.ascii                                   # uzunluk korur → aralıklar g'de de geçerli
    bulunan: dict[str, tuple[int, int]] = {}
    for sinyal, desen in S.items():
        x = re.search(desen, a)
        if x:
            bulunan[sinyal] = x.span()
    det = cikar(m)                                  # aralıklar maskeli girdiye göre (alıntı için)
    link = next((d for d in det if d.tip == "link"), None)

    talep = {"odeme_talebi", "kod_talebi", "kimlik_talebi"} & bulunan.keys()
    tehlike = bool(talep) or bool(tipler & SUPHELI_LINK) or {"yetki_iddiasi", "gizlilik_baskisi"} & bulunan.keys() \
        or "gizlilik_ifadesi" in tipler
    kanal_veya_link = "kanal_degistirme" in bulunan or link is not None
    if "odul_vaadi" in bulunan and kanal_veya_link and not re.search(REKLAM, a):
        tehlike = True                            # "video başı 40 TL kazan! Telegram'da…"
    if any(len(re.findall(d, a)) >= 2 for t, d in KONU.items() if t in ("yasa_disi_bahis", "yatirim_vip_grup",
                                                                       "gorev_is_ilani")) and kanal_veya_link:
        tehlike = True                            # güçlü dolandırıcılık konusu + yönlendirme
    if "paylasma_uyarisi" in tipler and not talep and not (tipler & SUPHELI_LINK):
        tehlike = False                           # "kodu kimseyle paylaşmayın" + istek yok → meşru bildirim

    if not tehlike:
        tur = "reklam_spam" if re.search(REKLAM, a) else "mesru_islem"
        kanitlar = []
    else:
        if "yetki_iddiasi" in bulunan:
            tur = "sahte_kamu_gorevlisi"
        elif "yakinlik_iddiasi" in bulunan and ({"odeme_talebi", "kod_talebi"} & bulunan.keys()):
            tur = "yakin_taklidi"
        else:
            puan = {t: len(re.findall(d, a)) for t, d in KONU.items()}
            en = max(puan, key=puan.get)
            tur = en if puan[en] > 0 else "kurum_taklidi"
        kanitlar = []
        sira = ["yetki_iddiasi", "yakinlik_iddiasi", "odeme_talebi", "kod_talebi", "kimlik_talebi", "odul_vaadi",
                "gizlilik_baskisi", "kanal_degistirme", "kurum_taklidi", "aciliyet"]
        for sinyal in sira:
            if sinyal in bulunan:
                p = _parca(g, *bulunan[sinyal])
                if len(p) >= 2 and all(p != k["alinti"] for k in kanitlar):
                    kanitlar.append({"alinti": p, "sinyal": sinyal})
        if link and len(kanitlar) < 3:
            kanitlar.append({"alinti": g[link.bas:link.bit], "sinyal": "link"})
        kanitlar = kanitlar[:3]
    return {"tur": tur, "kanitlar": kanitlar}
