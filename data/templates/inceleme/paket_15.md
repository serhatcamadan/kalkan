# Görev: Türkçe dolandırıcılık SMS ŞABLONLARININ denetimi

Sen bağımsız bir veri denetçisisin. Aşağıda 16 SENTETİK mesaj şablonu var; her biri için şablondan üretilmiş
2 örnek gösteriliyor. Bu şablonlardan küçük bir dil modeli eğitilecek. Hata şablondaysa YÜZLERCE örneğe yayılır,
bu yüzden ŞABLONU değerlendir. Kurum/marka adları, numaralar ve linkler UYDURMADIR.

## Her şablon için sırayla sor; "evet" dediğin İLK soruda karar ver
1. Gerçek hayatta böyle bir SMS/WhatsApp mesajı gelmesi akla yatkın DEĞİL mi (anlamca çelişkili, saçma)? → "cikar"
2. Tür AÇIKÇA yanlış mı, ya da mesaj BAŞKA bir türe en az bu kadar uyuyor mu? → "tur" (+ yeni_tur)
3. Türkçe dil hatası var mı (ek uyumu, çekim, anlam bozukluğu), ya da bir kanıt alıntısı yanındaki sinyalle
   AÇIKÇA uyuşmuyor mu, ya da ANA dolandırıcılık hamlesi kanıtlarda hiç yok mu? → "duzelt" (+ oneri)
4. Hiçbiri değilse → "dogru"

## Önemli kurallar
- Emin değilsen "dogru". Sadece AÇIK sorunları işaretle.
- BİLİNÇLİ gürültü hata DEĞİLDİR: Türkçe karaktersiz yazım, yazım hatası, BÜYÜK HARF, emoji, çift boşluk,
  [TEL] [IBAN] [OTP] [KART] maske etiketleri, "Ahmet Hanım" gibi rastgele ad-hitap eşleşmesi (bilinen, kapsam dışı).
- reklam_spam ve mesru_islem şablonlarında kanıt listesinin BOŞ olması doğrudur.
- Bazı şablonlar BİLEREK sınıflar arası tuzaktır: "kargo bedava" diyen reklam, şubede bekleyen gerçek kargo
  bildirimi, kod içeren meşru mesaj. Bunlar meşru/reklam ise doğrudur; dolandırıcılığa benzemeleri amaçlanmıştır.
- En fazla 3 kanıt seçilebilir; küçük ayrıntıların eksikliği hata değildir.

## Türler
- sahte_kargo_gumruk: Gerçek olmayan bir gönderi için gümrük, adres güncelleme veya teslim ücreti istenir. AYIRT EDİCİ: Meşru kargo bildirimi takip numarası verir ama ödeme veya kart bilgisi İSTEMEZ.
- kurum_taklidi: Banka, operatör, e-devlet veya platform gibi bir kurum adına hesap/kart sorunu bildirilir. AYIRT EDİCİ: Kurumlar SMS ile şifre/kart bilgisi istemez ve kendi alan adları dışında link vermez.
- sahte_kamu_gorevlisi: Polis, savcı, MASAK veya HERA/terör soruşturması bahanesiyle (çoğunlukla 60+) para veya kod istenir. AYIRT EDİCİ: Yetki/soruşturma iddiası ve gizlilik baskısı bir aradadır; kamu görevlisi para veya kod istemez.
- yatirim_vip_grup: Borsa, kripto veya döviz için "VIP sinyal grubu", garantili kazanç, aracı kurum taklidi. AYIRT EDİCİ: Karşılık bir yatırım/üyelik ve getiri vaadidir; çekiliş değil.
- yasa_disi_bahis: Lisanssız bahis/casino sitesi, deneme bonusu, şike/kesin maç tüyosu. AYIRT EDİCİ: Sürekli değişen giriş adresi ve bahis/casino terimleri.
- oyun_hesap_skin: Oyun hesabı, skin, oyun parası (CS2/Steam vb.) üzerinden hesap ele geçirme veya ödeme. AYIRT EDİCİ: Oyun platformu bağlamı ve hesap girişi/kod talebi.
- odul_kampanya: Kazanılmamış bir çekiliş, hediye, puan veya iade için küçük bir ücret ya da bilgi istenir. AYIRT EDİCİ: Kazanım iddiası + ödeme/bilgi talebi. Reklam bir şey satar, ödül tuzağı "kazandın" der.
- yakin_taklidi: Aile üyesi veya arkadaş gibi davranan, yeni numaradan acil para isteyen mesaj. AYIRT EDİCİ: Yakınlık hitabı + yeni numara + acil havale.
- gorev_is_ilani: Evden kolay iş, beğeni/yorum görevleri; önce küçük kazanç, sonra "seviye" için ödeme istenir. AYIRT EDİCİ: Karşılık bir iş/görevdir; ödeme "başlangıç/seviye ücreti" diye istenir.
- reklam_spam: İstenmeyen ama dolandırıcılık niteliği taşımayan ticari ileti. (zor negatif) AYIRT EDİCİ: Ödeme/kimlik/kod istemez; ret mekanizması içerir.
- mesru_islem: Gerçek tek kullanımlık şifre, kargo, randevu veya işlem bildirimi. (zor negatif) AYIRT EDİCİ: Bilgi verir, bir şey İSTEMEZ. "Kodu kimseyle paylaşmayın" uyarısı meşruiyet işaretidir.

## Sinyaller
- odeme_talebi: Para, ücret, havale/EFT veya kart ile ödeme talebi
- kod_talebi: Tek kullanımlık şifre, doğrulama veya Steam Guard kodunu paylaşma talebi
- kimlik_talebi: Şifre, TC no, kart bilgisi veya giriş yapma talebi
- aciliyet: Süre baskısı veya tehdit (24 saat, hemen, iptal edilecek)
- kurum_taklidi: Bir kurum/marka adına konuşma iddiası
- yetki_iddiasi: Polis, savcı, MASAK gibi resmi yetki iddiası
- odul_vaadi: Kazanç, hediye, bonus veya garantili getiri vaadi
- gizlilik_baskisi: Kimseye söyleme, bankayı arama gibi yalnızlaştırma
- kanal_degistirme: WhatsApp/Telegram grubuna geç, şu numarayı ara, uygulama kur
- yakinlik_iddiasi: Aile/arkadaş gibi hitap, yeni numara iddiası
- link: Tıklanması istenen bağlantı

## Çıktı biçimi (YALNIZCA geçerli bir JSON dizisi, başka metin yok; her şablon için tam bir öğe)
[{"id": "kargo_08", "karar": "dogru"},
 {"id": "kurum_09", "karar": "tur", "yeni_tur": "odul_kampanya", "not": "kısa gerekçe"},
 {"id": "gorev_10", "karar": "duzelt", "not": "kısa gerekçe", "oneri": "düzeltilmiş cümle"},
 {"id": "oyun_11", "karar": "cikar", "not": "kısa gerekçe"}]
"karar" ∈ dogru | tur | duzelt | cikar. "dogru" dışındaki her kararda "not" zorunlu.

## Şablonlar

### mesru_15
TÜR: mesru_islem
ÖRNEK 1: Mavibank: 377 lira tutarındaki havale talimatınızı onaylamak için tek kullanımlık şifreniz [OTP]. Bu şifreyi kimseyle paylaşmayın; Mavibank sizden şifre istemez.
  KANITLAR:
    (yok)
ÖRNEK 2: Mavibank: 552,50 lira tutarindaki havale talimatinizi onaylamak icin tek kullaimlik sifreniz [OTP]. Bu sifreyi kimseyle paylasmayin; Mavibank sizden sifre istemez.
  KANITLAR:
    (yok)

### mesru_16
TÜR: mesru_islem
ÖRNEK 1: Sepetgo: Siparişiniz alındı, sipariş tutarı 3.206₺. Kargoya verildiğinde size bilgi vereceğiz. Siparişlerim: sepetgo.com.tr/siparislerim
  KANITLAR:
    (yok)
ÖRNEK 2: 🎁 Çarşıla: Siparişiniz alındı, sipariş tutarı 1.093 TL. Kargoya verildiğinde size bilgi vereceğiz. Siparişlerim: https://carsila.com.tr/siparislerim
  KANITLAR:
    (yok)

### mesru_17
TÜR: mesru_islem
ÖRNEK 1: Nar Telekom: 19.10.2026 son ödeme tarihli 19,90 lira tutarındaki faturanız ödenmiştir. Teşekkür ederiz.
  KANITLAR:
    (yok)
ÖRNEK 2: 🎁 Turkuaz Mobil: 13.03.2026 son ödeme tarihli 145,90 TL tutarındaki faturanız ödenmiştir. Teşekkür ederiz.
  KANITLAR:
    (yok)

### mesru_18
TÜR: mesru_islem
ÖRNEK 1: e-Hizmet Kapısı: 17.10.2026 tarihli randevunuz oluşturulmuştur. Randevuya kimlik belgenizle gelmeniz gerekmektedir. İptal için kendi hesabınızdan işlem yapabilirsiniz.
  KANITLAR:
    (yok)
ÖRNEK 2: E-HİZMET KAPISI: 01.10.2026 TARİHLİ RANDEVUNUZ OLUŞTURULMUŞTUR. RANDEVUYA KİMLİK BELGENİZLE GELMENİZ GEREKMEKTEDİR. İPTAL İÇİN KENDİ HESABINIZDAN İŞLEM YAPABİLİRSİNİZ.
  KANITLAR:
    (yok)

### mesru_19
TÜR: mesru_islem
ÖRNEK 1: Kuzeykart: Kartınızla yapılan 4.222 TL tutarındaki internet alışverişi için doğrulama kodunuz [OTP]. Bu işlemi siz yapmıyorsanız kodu girmeyin ve kimseyle paylaşmayın.
  KANITLAR:
    (yok)
ÖRNEK 2: 🎁 Yonca Kart: Kartınızla yapılan 627  TL  tutarındaki internet  alışverişi  için  doğrulama kodunuz  [OTP]. Bu işlemi siz yapmıyorsanız  kodu  girmeyin  ve  kimseyle paylaşmayın.
  KANITLAR:
    (yok)

### mesru_20
TÜR: mesru_islem
ÖRNEK 1: Mavibank: Maaşınız 69.172 TL olarak hesabınıza yatırılmıştır. İyi günlerde kullanın.
  KANITLAR:
    (yok)
ÖRNEK 2: Ardicbank: Maasiniz 40.573 lira olarak hesabiniza yatirilmistir.  Iyi gunlerde kullanin.
  KANITLAR:
    (yok)

### mesru_21
TÜR: mesru_islem
ÖRNEK 1: Hızlıkargo: KG560318786 numaralı gönderiniz yarın gün içinde teslim edilecektir. Adresinizde olamayacaksanız www.hizlikargo.com.tr/teslimat sayfasından teslimat gününü değiştirebilirsiniz.
  KANITLAR:
    (yok)
ÖRNEK 2: Kumru Kargo: TK274501901 numaralı gönderiniz yarın gün içinde teslim edilecektir. Adresinizde olamayacaksanız https://kumrukargo.com.tr/teslimat sayfasından teslimat gününü değiştirebilirsiniz.
  KANITLAR:
    (yok)

### mesru_22
TÜR: mesru_islem
ÖRNEK 1: Çarşıla: 1.106 lira tutarındaki ödemeniz alınmıştır. Faturanıza www.carsila.com.tr/faturalarim adresinden ulaşabilirsiniz.
  KANITLAR:
    (yok)
ÖRNEK 2: Sepetgo: 3.423 TL tutarındaki ödemeniz alınmıştır. Faturranıza sepetgo.com.tr/faturalarim adresinden ulaşabilirsiniz.
  KANITLAR:
    (yok)

### mesru_23
TÜR: mesru_islem
ÖRNEK 1: Nar Telekom: Hattınıza 22.01.2026 tarihinde yeni bir cihaz tanımlandı. Bu işlem size ait değilse kimliğinizle en yakın mağazamıza başvurun.
  KANITLAR:
    (yok)
ÖRNEK 2: Nar Telekom: Hattınıza 09.01.2026 tarihinde yeni  bir  cihaz  tanımlandı.  Bu işlem size  ait değilse kimliğinizle en yakın mağazamıza  başvurun.
  KANITLAR:
    (yok)

### mesru_24
TÜR: mesru_islem
ÖRNEK 1: Ardıçbank: Kredi kartı başvurunuz onaylanmıştır. Kartınız birkaç iş günü içinde kayıtlı adresinize gönderilecek; teslim aldığınızda mobil uygulamamızdan aktifleştirebilirsiniz.
  KANITLAR:
    (yok)
ÖRNEK 2: Ardicbank: Kredi karti basvurunuz onaylanmistir. Kartiniz birkac is gunu icinde kayitli adresinize gonderilecek; teslim aldiginizda mobil uygulamamizdan aktiflestirebilirsiniz.
  KANITLAR:
    (yok)

### reklam_15
TÜR: reklam_spam
ÖRNEK 1: Turkuaz Mobil size özel: aylık 20 GB internet paketine geçin, ilk ay 37,00 TL! Detay: https://turkuazmobil.com.tr/kampanya Ret için IPTAL yazıp 3434'e gönderin.
  KANITLAR:
    (yok)
ÖRNEK 2: Nar Telekom size ozel: aylik 20 GB internet paketine gecin, ilk ay 91,50 TL! Detay: https://nartelekom.com.tr/kampanya Ret icin IPTAL yazip 7000'e gonderin.
  KANITLAR:
    (yok)

### reklam_16
TÜR: reklam_spam
ÖRNEK 1: Yonca Kart ile market alışverişlerinde %30 puan fırsatı 14.05.2026 tarihine kadar! Katılım için KATIL yazıp 2525'e gönderin. Ret: 7000
  KANITLAR:
    (yok)
ÖRNEK 2: Yonca Kart ile market alisverislerinde %20 puan firsati 02.06.2026 tarihine kadar! Katilim icin KATIL yazip 4848'e gonderin. Ret: 2525
  KANITLAR:
    (yok)

### reklam_17
TÜR: reklam_spam
ÖRNEK 1: Sepetgo Efsane Günler başladı! Elektronikte 2.494 TL'ye varan indirim ve 9 taksit. sepetgo.com.tr/kampanya İletişim izninizi 3434 ile iptal edebilirsiniz.
  KANITLAR:
    (yok)
ÖRNEK 2: Carsila Efsane Gunler basladi! Elektronikte 1.309 TL'ye varan indirim ve 9 taksit. carsila.com.tr/kampanya Iletisim izninizi 2525 ile iptal edebilirsiniz.
  KANITLAR:
    (yok)

### reklam_18
TÜR: reklam_spam
ÖRNEK 1: Yonca Kart: Akaryakıt alımlarınızda 13.05.2026 tarihine kadar 109,90 TL hediye puan. Kampanya koşulları: https://yoncakart.com.tr/kampanya Ret: 2525
  KANITLAR:
    (yok)
ÖRNEK 2: !!️ Yonca Kart: Akaryakıt alımlarınızda 03.04.2026 tarihine kadar 35,00 TL hediye puan. Kampanya koşulları: yoncakart.com.tr/kampanya Ret: 7000
  KANITLAR:
    (yok)

### reklam_19
TÜR: reklam_spam
ÖRNEK 1: Çarşıla üyesi olduğun için teşekkürler 💛 Bu hafta sepette ek %10 indirim kodun: TESEKKUR. Mersis: 0124604217861969 Ret: 4848
  KANITLAR:
    (yok)
ÖRNEK 2: SEPETGO ÜYESİ OLDUĞUN İÇİN TEŞEKKÜRLER 💛 BU HAFTA SEPETTE EK %30 İNDİRİM KODUN: TESEKKUR. MERSİS: 0688974300203258 RET: 7000
  KANITLAR:
    (yok)

### reklam_20
TÜR: reklam_spam
ÖRNEK 1: Turkuaz Mobil: Yeni sezon telefonlarda eski cihazını getir, 2.955 TL'ye varan değer kazan. Mağazalarımızda. SMS almamak için IPTAL yazıp 7000'e gönderin.
  KANITLAR:
    (yok)
ÖRNEK 2: Nar Telekom: Yeni sezon telefonlarda eski cihazini getir, 416 TL'ye varan deger kazan. Magazalarimizda. SMS almamak icin IPTAL yazip 4848'e gonderin.
  KANITLAR:
    (yok)
