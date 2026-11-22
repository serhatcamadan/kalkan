"""KALKAN · policy.py — risk ve öneri KODLA belirlenir                 v1.2 · 2026-11-22

v1.2: Model (veya kural) "meşru/reklam" dese bile mesajda IBAN varsa → ORTA. Gerekçe: kurumlar SMS/WhatsApp ile
      bir IBAN'a para göndermenizi istemez; IBAN hem PII hem kanıt (ADR-0003). Tetikleyen: kör set kor_13
      ("numaram değişti / acil 2.500 lazım / IBAN"), bu yüzden kor_13 artık KÖR DEĞİL. Bedeli ÖLÇÜLMEMİŞ: sentetik
      setlerde IBAN'lı meşru mesaj yok (0/690); gerçek hayatta arkadaş arası "IBAN'ım şu" mesajları alarm alır.

v1.1: "Reklam" diyen model + resmi olmayan link + yasal ret satırı yok → ORTA. Gerekçe taksonomide yazılı
      (reklam_spam: "ret mekanizması içerir"; TR'de ticari iletide İYS/ret zorunlu). Tetikleyen: adversarial adv_21
      (gpt-5.4-mini "reklam" dedi, kısa link vardı, düşük risk çıktı). Bu yüzden adv_21 artık KÖR DEĞİL.

Model risk üretmez. Risk = f(tür, kapıdan geçen kanıt, deterministik sinyaller, enjeksiyon lekesi).
Kırmızı çizgiler (testli):
  • Şema bozuk / zaman aşımı / model yok → BELIRSIZ (fail-closed), asla düşük değil.
  • Enjeksiyon lekesi → en az ORTA. Meşru bir kurum analiz aracına talimat vermez.
  • Model "meşru/reklam" dese bile güçlü deterministik işaret varsa → ORTA (güvenlik ağı: modelin yanılmasına karşı).
  • "Düşük" yalnızca: model dolandırıcılık dışı dedi + güçlü işaret yok + leke yok. Metni "işaret bulunamadı"dır.
"""
from __future__ import annotations

from dataclasses import dataclass

from .schema import DOLANDIRICILIK_DISI, DeterministikSinyal, DogrulanmisKanit, Risk, Tur

POLITIKA_SURUMU = "1.2"
GUCLU_SINYAL = {"marka_iceren_yabanci", "benzer_alan_adi", "punycode", "unicode_alan_adi", "gizli_karakter",
                "gizlilik_ifadesi"}
ORTA_SINYAL = {"kisa_link", "supheli_tld", "iban"}
TALEP = {"odeme_talebi", "kod_talebi", "kimlik_talebi"}

ONERI = {
    "sahte_kargo_gumruk": "Bağlantıya tıklamayın ve ödeme yapmayın. Gönderinizi kargo firmasının resmi uygulamasından takip numarasıyla kontrol edin.",
    "kurum_taklidi": "Bağlantıya tıklamayın; şifre, kart bilgisi veya kod paylaşmayın. Kurumu kendi bildiğiniz resmi numarasından ya da uygulamasından arayın.",
    "sahte_kamu_gorevlisi": "Polis, savcı veya başka bir kamu görevlisi telefonla para, altın ya da kod istemez. Görüşmeyi kapatın; 155 veya 156'yı arayın.",
    "yatirim_vip_grup": "Garantili kazanç vaadi dolandırıcılık işaretidir. Para göndermeyin; aracı kurumun SPK lisansını resmi kaynaktan kontrol edin.",
    "yasa_disi_bahis": "Lisanssız bahis ve 'kesin maç' teklifleri yasa dışıdır ve para kaybettirir. Bağlantıya tıklamayın, ödeme yapmayın.",
    "oyun_hesap_skin": "Oyun hesabı bilgilerinizi ve doğrulama kodunuzu kimseyle paylaşmayın. Yalnızca oyunun resmi sitesinden giriş yapın.",
    "odul_kampanya": "Katılmadığınız bir çekilişin ödülü için ücret ödemeyin, kart bilgisi girmeyin.",
    "yakin_taklidi": "Para göndermeden önce yakınınızı bildiğiniz ESKİ numarasından arayıp sesli teyit alın.",
    "gorev_is_ilani": "Önce ücret veya 'seviye' ödemesi isteyen iş teklifleri dolandırıcılıktır. Para göndermeyin.",
}
MESAJ = {
    "yuksek": "Bu mesajda belirgin dolandırıcılık işaretleri var.",
    "orta": "Bu mesajda dikkat gerektiren işaretler var.",
    "dusuk": "Belirgin bir dolandırıcılık işareti bulunamadı. Emin değilseniz gönderen kurumu resmi kanalından arayın.",
    "belirsiz": "Mesaj analiz edilemedi. Dikkatli olun: bağlantıya tıklamayın, kod veya ödeme paylaşmayın.",
}


@dataclass
class Karar:
    risk: Risk
    oneri_kodu: str
    mesaj: str
    gerekce: list[str]


def karar_ver(tur: Tur | None, kanitlar: list[DogrulanmisKanit], sinyaller: list[DeterministikSinyal],
              enjeksiyon: list[str]) -> Karar:
    tipler = {s.tip for s in sinyaller}
    guclu, orta = sorted(tipler & GUCLU_SINYAL), sorted(tipler & ORTA_SINYAL)
    gerekce = [f"sinyal:{x}" for x in guclu + orta] + [f"enjeksiyon:{x}" for x in enjeksiyon]

    if tur is None:
        return Karar(Risk.belirsiz, "BELIRSIZ_DIKKAT", MESAJ["belirsiz"], gerekce + ["model_cevabi_yok"])

    if tur not in DOLANDIRICILIK_DISI:
        talepli = any(k.sinyal.value in TALEP for k in kanitlar)
        risk = Risk.yuksek if (talepli or guclu or enjeksiyon) else Risk.orta
        if not kanitlar and not guclu:
            gerekce.append("model_dolandiricilik_dedi_kanit_yok")
        return Karar(risk, f"{tur.value.upper()}", f"{MESAJ[risk.value]} {ONERI[tur.value]}", gerekce)

    # model dolandırıcılık DIŞI dedi → güvenlik ağı
    resmi_olmayan_link = "link" in tipler and "resmi_alan_adi" not in tipler
    reklam_ama_retsiz = tur == Tur.reklam_spam and resmi_olmayan_link and "ret_mekanizmasi" not in tipler
    if reklam_ama_retsiz:
        gerekce.append("reklam_dedi_ama_ret_yok_ve_resmi_olmayan_link")
    iban_var = "iban" in tipler
    if iban_var:
        gerekce.append("dolandiricilik_disi_dedi_ama_iban_var")
    if guclu or enjeksiyon or reklam_ama_retsiz or iban_var or (orta and tur == Tur.mesru_islem and "kisa_link" in tipler):
        return Karar(Risk.orta, "CELISKI_DOGRULA",
                     f"{MESAJ['orta']} Bağlantıya tıklamadan veya bilgi paylaşmadan önce gönderenin resmi kanalından doğrulayın.",
                     gerekce + ["model_dolandiricilik_disi_dedi_ama_isaret_var"])
    return Karar(Risk.dusuk, "ISARET_YOK", MESAJ["dusuk"], gerekce)
