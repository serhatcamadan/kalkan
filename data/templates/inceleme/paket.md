# Görev: Türkçe dolandırıcılık SMS ŞABLONLARININ denetimi

Sen bağımsız bir veri denetçisisin. Aşağıda 77 SENTETİK mesaj şablonu var; her biri için şablondan üretilmiş
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

### bahis_08
TÜR: yasa_disi_bahis
ÖRNEK 1: golkral sitesinde %40 çevrimsiz yatırım bonusu! Spor, canlı casino, slot. golkral367.win
  KANITLAR:
    - odul_vaadi: "%40 çevrimsiz yatırım bonusu"
    - link: "golkral367.win"
ÖRNEK 2: betyildiz sitesinde %340 cevrimsiz yatirim bonusu! Spor, canli casino, slot. betyildiz925.com
  KANITLAR:
    - odul_vaadi: "%340 cevrimsiz yatirim bonusu"
    - link: "betyildiz925.com"

### bahis_09
TÜR: yasa_disi_bahis
ÖRNEK 1: Kupon tuttu mu? 😉 Bugünün banko maçları %90 tutturma oranıyla Kanalımıza katıl: chat.whatsapp.com/crAbaQAXUx VIP abonelik haftalık 1.457,50₺
  KANITLAR:
    - odul_vaadi: "Bugünün banko maçları %90 tutturma oranıyla"
    - kanal_degistirme: "Kanalımıza katıl: chat.whatsapp.com/crAbaQAXUx"
    - odeme_talebi: "VIP abonelik haftalık 1.457,50₺"
ÖRNEK 2: Kupon tuttu mu? 😉 Bugunun banko maclari %90 tutturma oraniyla Kanalimiza katil: https://t.me/golkralvip VIP abonelik haftalik 3.702,50 TL
  KANITLAR:
    - odul_vaadi: "Bugunun banko maclari %90 tutturma oraniyla"
    - kanal_degistirme: "Kanalimiza katil: https://t.me/golkralvip"
    - odeme_talebi: "VIP abonelik haftalik 3.702,50 TL"

### bahis_10
TÜR: yasa_disi_bahis
ÖRNEK 1: golkral: Para yatırma işleminizi 4.764,99₺ ile havale veya kripto üzerinden yapabilirsiniz. Erişim sorunu yaşıyorsanız güncel adres golkral643.com
  KANITLAR:
    - odeme_talebi: "Para yatırma işleminizi 4.764,99₺ ile havale veya kripto üzerinden"
    - link: "Erişim sorunu yaşıyorsanız güncel adres golkral643.com"
ÖRNEK 2: betyildiz: Para yatırma işleminizi 1.163₺ ile havale veya kripto üzerindn yapabilirsiniz. Erişim sorunu yaşıyorsanız güncel adres https://betyildiz313.xyz
  KANITLAR:
    - odeme_talebi: "Para yatırma işleminizi 1.163₺ ile havale veya kripto üzerindn yapabilirsiniz"
    - link: "Erişim sorunu yaşıyorsanız güncel adres https://betyildiz313.xyz"

### bahis_11
TÜR: yasa_disi_bahis
ÖRNEK 1: Hafta sonu derbisine özel 3.077 TL kombine sigortası, maç başlamadan katıl! golkral golkral271.xyz
  KANITLAR:
    - odul_vaadi: "3.077 TL kombine sigortası"
    - aciliyet: "maç başlamadan katıl"
    - link: "golkral271.xyz"
ÖRNEK 2: Hafta sonu derbisine ozel 1.045 TL kombine sigortasi, mac baslamadan katil! betyildiz betyildiz635.win
  KANITLAR:
    - odul_vaadi: "1.045 TL kombine sigortasi"
    - aciliyet: "mac baslamadan katil"
    - link: "betyildiz635.win"

### bahis_12
TÜR: yasa_disi_bahis
ÖRNEK 1: Ahmet Hanım, hesabınızdaki 2.141 lira bakiyeyi çekmek için çevrim tamamlama ücreti 113,50 TL yatırmanız gerekiyor. betyildiz canlı destek: [TEL]
  KANITLAR:
    - odul_vaadi: "2.141 lira bakiyeyi"
    - odeme_talebi: "çevrim tamamlama ücreti 113,50 TL yatırmanız gerekiyor"
    - kanal_degistirme: "[TEL]"
ÖRNEK 2: Gul Bey, hesabinizdaki 322 TL bakiyeyi cekmek icin cevrim tamamlama ucreti 74,00 TL yatirmaniz gerekiyor. golkral canli destek: [TEL]
  KANITLAR:
    - odul_vaadi: "322 TL bakiyeyi"
    - odeme_talebi: "cevrim tamamlama ucreti 74,00 TL yatirmaniz gerekiyor"
    - kanal_degistirme: "[TEL]"

### bahis_13
TÜR: yasa_disi_bahis
ÖRNEK 1: Rulet stratejisi: her gün 2.394 TL garantili kazanç. golkral sitesine şu linkle kayıt ol https://golkral162.xyz, davet kodu bugün geçerli.
  KANITLAR:
    - odul_vaadi: "her gün 2.394 TL garantili kazanç"
    - link: "şu linkle kayıt ol https://golkral162.xyz"
    - aciliyet: "davet kodu bugün geçerli"
ÖRNEK 2: Rulet  stratejisi: her  gün 4.412 TL garantili kazanç. betyildiz  sitesine şu  linkle  kayıt ol betyildiz888.win, davet kodu  bugün geçerli.
  KANITLAR:
    - odul_vaadi: "her  gün 4.412 TL garantili kazanç"
    - link: "şu  linkle  kayıt ol betyildiz888.win"
    - aciliyet: "davet kodu  bugün geçerli"

### bahis_14
TÜR: yasa_disi_bahis
ÖRNEK 1: Maç önü özel 🔥 kupabet ilk yatırımına 930,49 TL ekstra. Havale veya kripto ile 148,90₺ minimum Yeni giriş https://kupabet383.vip
  KANITLAR:
    - odul_vaadi: "ilk yatırımına 930,49 TL ekstra"
    - odeme_talebi: "Havale veya kripto ile 148,90₺ minimum"
    - link: "Yeni giriş https://kupabet383.vip"
ÖRNEK 2: MAÇ ÖNÜ ÖZEL 🔥 KUPABET İLK YATIRIMINA 4.916,50 TL EKSTRA. HAVALE VEYA KRİPTO İLE 118,90 LİRA MİNİMUM YENİ GİRİŞ KUPABET961.WİN
  KANITLAR:
    - odul_vaadi: "İLK YATIRIMINA 4.916,50 TL EKSTRA"
    - odeme_talebi: "HAVALE VEYA KRİPTO İLE 118,90 LİRA MİNİMUM"
    - link: "YENİ GİRİŞ KUPABET961.WİN"

### gorev_08
TÜR: gorev_is_ilani
ÖRNEK 1: Çarşıla iş ortaklığı: sipariş başına %40 komisyon, günlük 4.129₺ kazanç. Başvuru için WhatsApp [TEL]
  KANITLAR:
    - odul_vaadi: "sipariş başına %40 komisyon, günlük 4.129₺ kazanç"
    - kanal_degistirme: "Başvuru için WhatsApp [TEL]"
ÖRNEK 2: Sepetgo is ortakligi: siparis basina %50 komisyon, gunluk 1.677,90 TL kazanc. Basvuru icin WhatsApp [TEL]
  KANITLAR:
    - odul_vaadi: "siparis basina %50 komisyon, gunluk 1.677,90 TL kazanc"
    - kanal_degistirme: "Basvuru icin WhatsApp [TEL]"

### gorev_09
TÜR: gorev_is_ilani
ÖRNEK 1: Merhaba, insan kaynaklarından Can. Evden paketleme işi, parça başı 60,90 lira. Malzeme depozitosu 3.945 TL, iş bitince iade edilir.
  KANITLAR:
    - odul_vaadi: "Evden paketleme işi, parça başı 60,90 lira"
    - odeme_talebi: "Malzeme depozitosu 3.945 TL"
ÖRNEK 2: Merhaba, insan kaynaklarından Emre. Evden paketleme işi, parça başı 72,90 TL. Malzeme depoitosu 729 TL, iş biince iade edilir.
  KANITLAR:
    - odul_vaadi: "Evden paketleme işi, parça başı 72,90 TL"
    - odeme_talebi: "Malzeme depoitosu 729 TL"

### gorev_10
TÜR: gorev_is_ilani
ÖRNEK 1: Görev listesi hazır: 3 uygulamayı indir ve puanla, 89,90 TL kazan. Ödemeni almak için gruptaki asistana yaz chat.whatsapp.com/9hv8u7T8JA
  KANITLAR:
    - odul_vaadi: "3 uygulamayı indir ve puanla, 89,90 TL kazan"
    - kanal_degistirme: "Ödemeni almak için gruptaki asistana yaz chat.whatsapp.com/9hv8u7T8JA"
ÖRNEK 2: Gorev  listesi hazir: 3 uygulamayi indir ve puanla,  116,99₺  kazan.  Odemeni almak  icin gruptaki asistana yaz  t.me/+ucoYeMz09h
  KANITLAR:
    - odul_vaadi: "3 uygulamayi indir ve puanla,  116,99₺  kazan"
    - kanal_degistirme: "Odemeni almak  icin gruptaki asistana yaz  t.me/+ucoYeMz09h"

### gorev_11
TÜR: gorev_is_ilani
ÖRNEK 1: Oğuz Bey, kazancınız 59.455 TL oldu fakat çekim için hesabınızın 4.326,90 TL bakiye ile doğrulanması gerekiyor. 2 saat içinde
  KANITLAR:
    - odul_vaadi: "kazancınız 59.455 TL oldu"
    - odeme_talebi: "çekim için hesabınızın 4.326,90 TL bakiye ile doğrulanması gerekiyor"
    - aciliyet: "2 saat içinde"
ÖRNEK 2: 🔔 Çağa Bey, kazancınız 88.645 TL oldu fakat çekim için hesabınızn 4.942 TL bakiye ile doğrulanması gerekiyor. 1 saat içide
  KANITLAR:
    - odul_vaadi: "kazancınız 88.645 TL oldu"
    - odeme_talebi: "çekim için hesabınızn 4.942 TL bakiye ile doğrulanması gerekiyor"
    - aciliyet: "1 saat içide"

### gorev_12
TÜR: gorev_is_ilani
ÖRNEK 1: Kargo firması için evden adres etiketi yazma işi, haftalık 2.195 TL. Başvuru dosya ücreti 115,50₺ www.sepetgo-destek.live/dogrula
  KANITLAR:
    - odul_vaadi: "evden adres etiketi yazma işi, haftalık 2.195 TL"
    - odeme_talebi: "Başvuru dosya ücreti 115,50₺"
    - link: "www.sepetgo-destek.live/dogrula"
ÖRNEK 2: Kargo firmasi icin evden adres etiketi yazma isi, haftalik 445₺. Basvuru dosya ucreti 89,50 TL www.carsila-guvenlik.rest/dogrula
  KANITLAR:
    - odul_vaadi: "evden adres etiketi yazma isi, haftalik 445₺"
    - odeme_talebi: "Basvuru dosya ucreti 89,50 TL"
    - link: "www.carsila-guvenlik.rest/dogrula"

### gorev_13
TÜR: gorev_is_ilani
ÖRNEK 1: Sosyal medya hesabınızı inceledik 🙌 Marka elçisi olarak ayda 37.049 TL kazanabilirsiniz. Detaylar için menajerimize yazın chat.whatsapp.com/5vNWrvnOnD
  KANITLAR:
    - odul_vaadi: "Marka elçisi olarak ayda 37.049 TL kazanabilirsiniz"
    - kanal_degistirme: "Detaylar için menajerimize yazın chat.whatsapp.com/5vNWrvnOnD"
ÖRNEK 2: Sosyal medya hesabınızı inceledik 🙌 Marka eçisi olarak ayda 15.248 TL kazanabilirsiniz. Detaylar için menajerimize yazın https://t.me/sepetgovip
  KANITLAR:
    - odul_vaadi: "Marka eçisi olarak ayda 15.248 TL kazanabilirsiniz"
    - kanal_degistirme: "Detaylar için menajerimize yazın https://t.me/sepetgovip"

### gorev_14
TÜR: gorev_is_ilani
ÖRNEK 1: Pazarcık anket ekibi: doldurduğunuz her form için 70,50 TL. Üyelik aktivasyonu 2.102,99 TL Koordinatör: [TEL]
  KANITLAR:
    - odul_vaadi: "doldurduğunuz her form için 70,50 TL"
    - odeme_talebi: "Üyelik aktivasyonu 2.102,99 TL"
    - kanal_degistirme: "Koordinatör: [TEL]"
ÖRNEK 2: Pazarcik urun test ekibi: doldurdugunuz her form icin 104,99 TL. Uyelik aktivasyonu 2.883,49 TL Koordinator: [TEL]
  KANITLAR:
    - odul_vaadi: "doldurdugunuz her form icin 104,99 TL"
    - odeme_talebi: "Uyelik aktivasyonu 2.883,49 TL"
    - kanal_degistirme: "Koordinator: [TEL]"

### kamu_08
TÜR: sahte_kamu_gorevlisi
ÖRNEK 1: Sayın Murat Bey, ben Cumhuriyet Savcısıyım, dosyanız bende. Görüntülü görüşme için WhatsApp'tan [TEL] numarasına yazın. Bu görüşmeyi kimseyle paylaşmanız yasaktır.
  KANITLAR:
    - yetki_iddiasi: "ben Cumhuriyet Savcısıyım, dosyanız bende"
    - kanal_degistirme: "Görüntülü görüşme için WhatsApp'tan [TEL] numarasına yazın"
    - gizlilik_baskisi: "Bu görüşmeyi kimseyle paylaşmanız yasaktır"
ÖRNEK 2: SAYIN İSMAİL BEY, BEN CUMHURİYET SAVCISIYIM, DOSYANIZ BENDE. GÖRÜNTÜLÜ GÖRÜŞME İÇİN WHATSAPP'TAN [TEL] NUMARASINA YAZIN. BU GÖRÜŞMEYİ KİMSEYLE PAYLAŞMANIZ YASAKTIR.
  KANITLAR:
    - yetki_iddiasi: "BEN CUMHURİYET SAVCISIYIM, DOSYANIZ BENDE"
    - kanal_degistirme: "GÖRÜNTÜLÜ GÖRÜŞME İÇİN WHATSAPP'TAN [TEL] NUMARASINA YAZIN"
    - gizlilik_baskisi: "BU GÖRÜŞMEYİ KİMSEYLE PAYLAŞMANIZ YASAKTIR"

### kamu_09
TÜR: sahte_kamu_gorevlisi
ÖRNEK 1: Teyze, biz polisiz, evinizin önündeki ekip bizden. Evdeki altınları ve dövizi poşete koyup kapıdaki memura verin, şebeke bu gece gelecek.
  KANITLAR:
    - yetki_iddiasi: "biz polisiz, evinizin önündeki ekip bizden"
    - odeme_talebi: "Evdeki altınları ve dövizi poşete koyup kapıdaki memura verin"
    - aciliyet: "şebeke bu gece gelecek"
ÖRNEK 2: 🎁 Teyze, biz polisiz, evinizin onundeki ekip bizden. Evdeki altinlari ve dovizi posete koyup kapidaki memura verin, sebeke bu gece gelecek.
  KANITLAR:
    - yetki_iddiasi: "biz polisiz, evinizin onundeki ekip bizden"
    - odeme_talebi: "Evdeki altinlari ve dovizi posete koyup kapidaki memura verin"
    - aciliyet: "sebeke bu gece gelecek"

### kamu_10
TÜR: sahte_kamu_gorevlisi
ÖRNEK 1: Vergi Denetim Kurulu müfettişi Çağla: adınıza sahte fatura düzenlenmiş. Hesabınızdaki parayı soruşturma bitene kadar [IBAN] numaralı kamu hesabına aktarın. Avukatınızla dahi konuşmayın.
  KANITLAR:
    - yetki_iddiasi: "Vergi Denetim Kurulu müfettişi Çağla"
    - odeme_talebi: "Hesabınızdaki parayı soruşturma bitene kadar [IBAN] numaralı kamu hesabına"
    - gizlilik_baskisi: "Avukatınızla dahi konuşmayın"
ÖRNEK 2: Vergi Denetim Kurulu mufettisi Burak: adiniza sahte fatura duzenlenmis. Hesabinizdaki parayi sorusturma bitene kadar [IBAN] numarali kamu hesabina aktarin. Avukatinizla dahi konusmayin.
  KANITLAR:
    - yetki_iddiasi: "Vergi Denetim Kurulu mufettisi Burak"
    - odeme_talebi: "Hesabinizdaki parayi sorusturma bitene kadar [IBAN] numarali kamu hesabina"
    - gizlilik_baskisi: "Avukatinizla dahi konusmayin"

### kamu_11
TÜR: sahte_kamu_gorevlisi
ÖRNEK 1: Siber Polis: hattınız bir dolandırıcılık olayında kullanıldı. Hattınızın kapatılmaması için gelen SMS kodunu memura söyleyin 1 saat içinde
  KANITLAR:
    - yetki_iddiasi: "Siber Polis: hattınız bir dolandırıcılık olayında kullanıldı"
    - kod_talebi: "Hattınızın kapatılmaması için gelen SMS kodunu memura söyleyin"
    - aciliyet: "1 saat içinde"
ÖRNEK 2: SİBER POLİS: HATTINIZ BİR DOLANDIRICILIK OLAYINDA KULLANILDI. HATTINIZIN KAPATILMAMASI İÇİN GELEN SMS KODUNU MEMURA SÖYLEYİN 1 SAAT İÇİNDE
  KANITLAR:
    - yetki_iddiasi: "SİBER POLİS: HATTINIZ BİR DOLANDIRICILIK OLAYINDA KULLANILDI"
    - kod_talebi: "HATTINIZIN KAPATILMAMASI İÇİN GELEN SMS KODUNU MEMURA SÖYLEYİN"
    - aciliyet: "1 SAAT İÇİNDE"

### kamu_12
TÜR: sahte_kamu_gorevlisi
ÖRNEK 1: Lacivert Bank hesabınızla ilgili Jandarma Siber birimi olarak arıyoruz. Kimliğinizi doğrulamak için internet bankacılığı şifrenizi söyleyin, bankayı aramayın, onlar da şüpheli.
  KANITLAR:
    - yetki_iddiasi: "Jandarma Siber birimi olarak arıyoruz"
    - kimlik_talebi: "Kimliğinizi doğrulamak için internet bankacılığı şifrenizi söyleyin"
    - gizlilik_baskisi: "bankayı aramayın, onlar da şüpheli"
ÖRNEK 2: Ardicbank hesabinizla ilgili Jandarma Siber birimi olarak ariyoruz. Kimliginizi dogrulamak icin internet bankaciligi sifrenizi soyleyin, bankayi aramayin, onlar da supheli.
  KANITLAR:
    - yetki_iddiasi: "Jandarma Siber birimi olarak ariyoruz"
    - kimlik_talebi: "Kimliginizi dogrulamak icin internet bankaciligi sifrenizi soyleyin"
    - gizlilik_baskisi: "bankayi aramayin, onlar da supheli"

### kamu_13
TÜR: sahte_kamu_gorevlisi
ÖRNEK 1: Ben Başsavcılıktan Savcı Çağla, telefonla ifadenizi alacağım. Kimlik teyidi için size gelen 6 haneli kodu söyleyin. İfade gizlidir, ailenize anlatmayın.
  KANITLAR:
    - yetki_iddiasi: "Ben Başsavcılıktan Savcı Çağla, telefonla ifadenizi alacağım"
    - kod_talebi: "Kimlik teyidi için size gelen 6 haneli kodu söyleyin"
    - gizlilik_baskisi: "İfade gizlidir, ailenize anlatmayın"
ÖRNEK 2: BEN BAŞSAVCILIKTAN SAVCI EMRE, TELEFONLA İFADENİZİ ALACAĞIM. KİMLİK TEYİDİ İÇİN SİZE GELEN 6 HANELİ KODU SÖYLEYİN. İFADE GİZLİDİR, AİLENİZE ANLATMAYIN.
  KANITLAR:
    - yetki_iddiasi: "BEN BAŞSAVCILIKTAN SAVCI EMRE, TELEFONLA İFADENİZİ ALACAĞIM"
    - kod_talebi: "KİMLİK TEYİDİ İÇİN SİZE GELEN 6 HANELİ KODU SÖYLEYİN"
    - gizlilik_baskisi: "İFADE GİZLİDİR, AİLENİZE ANLATMAYIN"

### kamu_14
TÜR: sahte_kamu_gorevlisi
ÖRNEK 1: Merhaba, Terörle Mücadele Şube'den Başkomiser Deniz. Kimliğinizle açılmış hesaplar var. Sizi birazdan [TEL] numarasından savcımız arayacak, telefonu kapatmayın ve kimseye haber vermeyin.
  KANITLAR:
    - yetki_iddiasi: "Terörle Mücadele Şube'den Başkomiser Deniz"
    - kanal_degistirme: "Sizi birazdan [TEL] numarasından savcımız arayacak"
    - gizlilik_baskisi: "telefonu kapatmayın ve kimseye haber vermeyin"
ÖRNEK 2: Merhaba, Terorle Mucadele Sube'den Baskomiser Selin. Kimliginizle acilmis hesaplar var. Sizi birazdan [TEL] numarasindan savcimiz arayacak, telefonu kapatmayin ve kimseye haber vermeyin.
  KANITLAR:
    - yetki_iddiasi: "Terorle Mucadele Sube'den Baskomiser Selin"
    - kanal_degistirme: "Sizi birazdan [TEL] numarasindan savcimiz arayacak"
    - gizlilik_baskisi: "telefonu kapatmayin ve kimseye haber vermeyin"

### kargo_08
TÜR: sahte_kargo_gumruk
ÖRNEK 1: Hızlıkargo: Teslimat adresinizde hata tespit edildi, gönderiniz depoda bekletiliyor. Adresinizi onaylayın: t.ly/rrHBLyT Yeniden gönderim ücreti 127,90 TL
  KANITLAR:
    - link: "Adresinizi onaylayın: t.ly/rrHBLyT"
    - odeme_talebi: "Yeniden gönderim ücreti 127,90 TL"
ÖRNEK 2: Hizlikargo: Teslimat adresinizde eksiklik tespit edildi, gonderiniz depoda bekletiliyor. Adresinizi onaylayin: https://bit.ly/ELg9H Yeniden gonderim ucreti 51,90 TL
  KANITLAR:
    - link: "Adresinizi onaylayin: https://bit.ly/ELg9H"
    - odeme_talebi: "Yeniden gonderim ucreti 51,90 TL"

### kargo_09
TÜR: sahte_kargo_gumruk
ÖRNEK 1: İyi günler, Hızlıkargo kuryesiyim. SP537491295 nolu paketiniz için 98,99₺ eksik posta ücreti çıktı. Ödeme için WhatsApp'tan [TEL] numarasına yazın, bugün yapılmazsa paket iade edilir.
  KANITLAR:
    - odeme_talebi: "98,99₺ eksik posta ücreti çıktı"
    - kanal_degistirme: "Ödeme için WhatsApp'tan [TEL] numarasına yazın"
    - aciliyet: "bugün yapılmazsa paket iade edilir"
ÖRNEK 2: Merhaba,  Kumru Kargo kuryesiyim.  TK465093487 nolu paketiniz  icin 98,99₺  eksik posta ucreti cikti.  Odeme icin WhatsApp'tan  [TEL]  numarasina yazin, bugun yapilmazsa  paket  iade  edilir.
  KANITLAR:
    - odeme_talebi: "98,99₺  eksik posta ucreti cikti"
    - kanal_degistirme: "Odeme icin WhatsApp'tan  [TEL]  numarasina yazin"
    - aciliyet: "bugun yapilmazsa  paket  iade  edilir"

### kargo_10
TÜR: sahte_kargo_gumruk
ÖRNEK 1: Hızlıkargo Bilgi: TK135744596 sayılı gönderi için gümrük beyannamesi hazırlandı. Vergi tutarı 4.197,99 TL, [IBAN] hesabına yatırılmalıdır. Açıklamaya takip numaranızı yazınız. 12 saat içinde ödenmezse gönderi iade edilir
  KANITLAR:
    - odeme_talebi: "Vergi tutarı 4.197,99 TL, [IBAN] hesabına yatırılmalıdır"
    - aciliyet: "12 saat içinde ödenmezse gönderi iade edilir"
ÖRNEK 2: Kumru Kargo Bilgi: KG597884419 sayili gonderi icin gumruk beyannamesi duzenlendi. Vergi tutari 1.669,00 TL, [IBAN] hesabina yatirilmalidir. Aciklamaya takip numaranizi yaziniz. 1 saat icinde odenmezse gonderi iade edilir
  KANITLAR:
    - odeme_talebi: "Vergi tutari 1.669,00 TL, [IBAN] hesabina yatirilmalidir"
    - aciliyet: "1 saat icinde odenmezse gonderi iade edilir"

### kargo_11
TÜR: sahte_kargo_gumruk
ÖRNEK 1: Paketiniz teslim edilemedi. 65,90 TL ödeyip yeni teslim tarihi seçin: rebrand.ly/ORC1t -Hızlıkargo
  KANITLAR:
    - odeme_talebi: "65,90 TL ödeyip yeni teslim tarihi seçin"
    - link: "rebrand.ly/ORC1t"
ÖRNEK 2: Paketiiniz teslim edilemedi. 96,00 TL odeyyip yeni teslim tarihi secin: https://cutt.ly/Gof62Y -Hizlikargo
  KANITLAR:
    - odeme_talebi: "96,00 TL odeyyip yeni teslim tarihi secin"
    - link: "https://cutt.ly/Gof62Y"

### kargo_12
TÜR: sahte_kargo_gumruk
ÖRNEK 1: www.kumrukargo-tr.monster/dogrula adresinden kimlik ve kart bilgilerinizi doğrulamadığınız sürece Kumru Kargo gönderiniz teslim edilmeyecektir. Sistem bugün saat 15:00 itibarıyla kapanacak.
  KANITLAR:
    - link: "www.kumrukargo-tr.monster/dogrula"
    - kimlik_talebi: "kimlik ve kart bilgilerinizi doğrulamadığınız sürece"
    - aciliyet: "Sistem bugün saat 15:00 itibarıyla kapanacak"
ÖRNEK 2: 📦 http://hizlikargo-guvenlik.top/odeme adresinden kimlik ve kart bilgilerinizi doğrulamadığınız sürece Hızlıkargo gönderiniz teslim edilmeyecektir. Sistem bugün saat 09:00 itibarıyla kapanacak.
  KANITLAR:
    - link: "http://hizlikargo-guvenlik.top/odeme"
    - kimlik_talebi: "kimlik ve kart bilgilerinizi doğrulamadığınız sürece"
    - aciliyet: "Sistem bugün saat 09:00 itibarıyla kapanacak"

### kargo_13
TÜR: sahte_kargo_gumruk
ÖRNEK 1: Çarşıla siparişiniz Hızlıkargo gümrük deposuna ulaştı. Teslimat için 130,00 TL gümrük vergisi gerekiyor, ödeme bağlantısı http://hizlikargogiris.vip/giris 24 saat sonra gönderi imha edilir
  KANITLAR:
    - odeme_talebi: "Teslimat için 130,00 TL gümrük vergisi gerekiyor"
    - link: "ödeme bağlantısı http://hizlikargogiris.vip/giris"
    - aciliyet: "24 saat sonra gönderi imha edilir"
ÖRNEK 2: ÇARŞILA SİPARİŞİNİZ KUMRU KARGO GÜMRÜK DEPOSUNA ULAŞTI. TESLİMAT İÇİN 37,49 LİRA GÜMRÜK VERGİSİ GEREKİYOR, ÖDEME BAĞLANTISI HTTP://KUMRUKARGO-İADE.VİP/4095 48 SAAT SONRA GÖNDERİ İMHA EDİLİR
  KANITLAR:
    - odeme_talebi: "TESLİMAT İÇİN 37,49 LİRA GÜMRÜK VERGİSİ GEREKİYOR"
    - link: "ÖDEME BAĞLANTISI HTTP://KUMRUKARGO-İADE.VİP/4095"
    - aciliyet: "48 SAAT SONRA GÖNDERİ İMHA EDİLİR"

### kargo_14
TÜR: sahte_kargo_gumruk
ÖRNEK 1: Sevgili müşterimiz, Serçe Lojistik aracımız bugün adresinize uğradı ancak kimseye ulaşamadı. Teslim saatini ayarlamak için [TEL] numaralı hatta mesaj atın, randevu ücreti 24,50 TL kartla alınır.
  KANITLAR:
    - kanal_degistirme: "Teslim saatini ayarlamak için [TEL] numaralı hatta mesaj atın"
    - odeme_talebi: "randevu ücreti 24,50 TL kartla alınır"
ÖRNEK 2: Sevgili musterimiz, Serce Lojistik aracimiz bugun adresinize ugradi ancak kimseye ulasamadi. Teslim saatini ayarlamak icin [TEL] numarali hatta mesaj atin, randevu ucreti 77,99₺ kartla alinir.
  KANITLAR:
    - kanal_degistirme: "Teslim saatini ayarlamak icin [TEL] numarali hatta mesaj atin"
    - odeme_talebi: "randevu ucreti 77,99₺ kartla alinir"

### kurum_08
TÜR: kurum_taklidi
ÖRNEK 1: e-Hizmet Kapısı: Adınıza kesilmiş 110,99 TL tutarında ödenmemiş trafik cezası bulunmaktadır. 2 saat içinde ödenmezse ceza iki katına çıkar. Ödeme: https://eihzmetkapisi.vip/odeme
  KANITLAR:
    - kurum_taklidi: "110,99 TL tutarında ödenmemiş trafik cezası bulunmaktadır"
    - aciliyet: "2 saat içinde ödenmezse ceza iki katına çıkar"
    - link: "Ödeme: https://eihzmetkapisi.vip/odeme"
ÖRNEK 2: 🔔 e-Hizmet Kapısı: Adınıza kesilmiş 102,90 TL tutarında ödenmemiş trafik cezası bulunmaktadır. 12 saat içinde ödenmezse ceza iki katına çıkar. Ödeme: ehizmetkapisi-tr.loan/giris
  KANITLAR:
    - kurum_taklidi: "102,90 TL tutarında ödenmemiş trafik cezası bulunmaktadır"
    - aciliyet: "12 saat içinde ödenmezse ceza iki katına çıkar"
    - link: "Ödeme: ehizmetkapisi-tr.loan/giris"

### kurum_09
TÜR: kurum_taklidi
ÖRNEK 1: Sepetgo: 1.801,90 TL tutarındaki iadeniz onaylandı ancak kart bilgileriniz doğrulanamadı. İadeyi almak için esepetgo.cyou/giris 1 saat içinde işlem yapılmazsa iade iptal olur
  KANITLAR:
    - kimlik_talebi: "kart bilgileriniz doğrulanamadı"
    - link: "İadeyi almak için esepetgo.cyou/giris"
    - aciliyet: "1 saat içinde işlem yapılmazsa iade iptal olur"
ÖRNEK 2: Sepetgo: 4.188₺ tutarıındaki iadeniz onaylandı ancak kart bilgilerriniz doğrulanamadı. İadeyi almak için www.seeptgo.cyou/odeme 3 gün içinde işlem yapılmazsa iade iptal olur
  KANITLAR:
    - kimlik_talebi: "kart bilgilerriniz doğrulanamadı"
    - link: "İadeyi almak için www.seeptgo.cyou/odeme"
    - aciliyet: "3 gün içinde işlem yapılmazsa iade iptal olur"

### kurum_10
TÜR: kurum_taklidi
ÖRNEK 1: Sayın abonemiz, Nar Telekom hattınızın kayıt süresi dolmuştur. Hattınızın kapanmaması için kimlik numaranızı ve doğum tarihinizi www[.]nartelekom-destek.net/tr/islem üzerinden girin. Son gün 13.12.2026
  KANITLAR:
    - kurum_taklidi: "Nar Telekom hattınızın kayıt süresi dolmuştur"
    - kimlik_talebi: "Hattınızın kapanmaması için kimlik numaranızı ve doğum tarihinizi"
    - aciliyet: "Son gün 13.12.2026"
ÖRNEK 2: Sayin abonemiz, Turkuaz Mobil hattinizin kayit suresi dolmustur. Hattinizin kapanmamasi icin kimlik numaranizi ve dogum tarihinizi turkuazmobil-guvenlik.monster/tr/islem uzerinden girin. Son gun 10.03.2026
  KANITLAR:
    - kurum_taklidi: "Turkuaz Mobil hattinizin kayit suresi dolmustur"
    - kimlik_talebi: "Hattinizin kapanmamasi icin kimlik numaranizi ve dogum tarihinizi"
    - aciliyet: "Son gun 10.03.2026"

### kurum_11
TÜR: kurum_taklidi
ÖRNEK 1: Kuzeykart: 315,50 TL limit artışı talebiniz alındı. Talebi iptal etmek için size gelen kodu [TEL] numarasına SMS ile gönderin 48 saat içinde
  KANITLAR:
    - kod_talebi: "Talebi iptal etmek için size gelen kodu [TEL] numarasına SMS ile gönderin"
    - aciliyet: "48 saat içinde"
ÖRNEK 2: Yonca Kart: 4.924 TL limit artisi talebiniz alindi. Talebi iptal etmek icin size gelen kodu [TEL] numarasina SMS ile gonderin 48 saat icinde
  KANITLAR:
    - kod_talebi: "Talebi iptal etmek icin size gelen kodu [TEL] numarasina SMS ile gonderin"
    - aciliyet: "48 saat icinde"

### kurum_12
TÜR: kurum_taklidi
ÖRNEK 1: Mavibank Müşteri Hizmetleri: hesabınıza yurt dışından giriş denemesi yapıldı. Güvenlik ekibimizle görüşmek için [TEL] numarasını arayın, 1 saat içinde aramazsanız kartınız iptal edilecek.
  KANITLAR:
    - kurum_taklidi: "hesabınıza yurt dışından giriş denemesi yapıldı"
    - kanal_degistirme: "Güvenlik ekibimizle görüşmek için [TEL] numarasını arayın"
    - aciliyet: "1 saat içinde aramazsanız kartınız iptal edilecek"
ÖRNEK 2: LACIVERT BANK MUSTERI HIZMETLERI: HESABINIZA YURT DISINDAN GIRIS DENEMESI YAPILDI. GUVENLIK EKIBIMIZLE GORUSMEK ICIN [TEL] NUMARASINI ARAYIN, 3 GUN ICINDE ARAMAZSANIZ KARTINIZ IPTAL EDILECEK.
  KANITLAR:
    - kurum_taklidi: "HESABINIZA YURT DISINDAN GIRIS DENEMESI YAPILDI"
    - kanal_degistirme: "GUVENLIK EKIBIMIZLE GORUSMEK ICIN [TEL] NUMARASINI ARAYIN"
    - aciliyet: "3 GUN ICINDE ARAMAZSANIZ KARTINIZ IPTAL EDILECEK"

### kurum_13
TÜR: kurum_taklidi
ÖRNEK 1: e-Hizmet Kapısı bildirimi: adınıza düzenlenen elektronik tebligat teslim edilemedi. Tebligatı görüntülemek için T.C. kimlik numaranız ve şifrenizle giriş yapın https://bit.ly/uHyPVt
  KANITLAR:
    - kurum_taklidi: "adınıza düzenlenen elektronik tebligat teslim edilemedi"
    - kimlik_talebi: "Tebligatı görüntülemek için T.C. kimlik numaranız ve şifrenizle giriş yapın"
    - link: "https://bit.ly/uHyPVt"
ÖRNEK 2: !!️ e-Hizmet Kaapısı bildirimi: adınıza düzenlenen elektronik tebligat tesllim edilemedi. Tebligatı görüntülemek için T.C. kimlik numaranız ve şifrenizle giriş yapın t.co/XPW0EtkS
  KANITLAR:
    - kurum_taklidi: "adınıza düzenlenen elektronik tebligat tesllim edilemedi"
    - kimlik_talebi: "Tebligatı görüntülemek için T.C. kimlik numaranız ve şifrenizle giriş yapın"
    - link: "t.co/XPW0EtkS"

### kurum_14
TÜR: kurum_taklidi
ÖRNEK 1: Lodos Mobil: faturanız iki kez tahsil edildiği için 120,90₺ iade edilecektir. İade için kart numaranızı ve son kullanma tarihini www.elodosmobil.shop/3967 adresine girin.
  KANITLAR:
    - kurum_taklidi: "faturanız iki kez tahsil edildiği için 120,90₺ iade edilecektir"
    - kimlik_talebi: "İade için kart numaranızı ve son kullanma tarihini"
    - link: "www.elodosmobil.shop/3967"
ÖRNEK 2: Lodos Mobil: faturaniz iki kez tahsil edildigi icin 145,90 lira iade edilecektir. Iade icin kart numaranizi ve son kullanma tarihini http://lodosmobil-tr.shop/tr/islem adresine girin.
  KANITLAR:
    - kurum_taklidi: "faturaniz iki kez tahsil edildigi icin 145,90 lira iade edilecektir"
    - kimlik_talebi: "Iade icin kart numaranizi ve son kullanma tarihini"
    - link: "http://lodosmobil-tr.shop/tr/islem"

### mesru_08
TÜR: mesru_islem
ÖRNEK 1: Hızlıkargo: TK975055509 numaralı gönderiniz adresinizde teslim edilemediği için şubemize bırakılmıştır. Kimliğinizle 3 iş günü içinde şubeden teslim alabilirsiniz.
  KANITLAR:
    (yok)
ÖRNEK 2: Hızlıkargo: KG395350400 numaralı gönderiniz adresinizde teslim edilemediği için şubemize bırakılmıştır. Kimliiğnizle 3 iş günü içinde şubeden teslim alabilirsiniz.
  KANITLAR:
    (yok)

### mesru_09
TÜR: mesru_islem
ÖRNEK 1: Mavibank: İnternet şubesi şifreniz 05.09.2026 08:00 tarihinde değiştirilmiştir. Bu işlemi siz yapmadıysanız mobil uygulamamızdaki Müşteri Hizmetleri bölümünden bize ulaşın.
  KANITLAR:
    (yok)
ÖRNEK 2: ⚠️ Lacivert Bank: İnternet şubesi şifreniz 08.04.2026 10:30 tarihinde değiştirilmiştir. Bu işlemi siz yapmadıysanız mobil uygulamamızdaki Müşteri Hizmetleri bölümünden bize ulaşın.
  KANITLAR:
    (yok)

### mesru_10
TÜR: mesru_islem
ÖRNEK 1: Turkuaz Mobil: 08.06.2026 itibarıyla aylık paketiniz yenilenmiştir. Kalan kullanım hakkınızı https://turkuazmobil.com.tr/takip adresinden veya uygulamamızdan görebilirsiniz.
  KANITLAR:
    (yok)
ÖRNEK 2: Nar Telekom: 11.08.2026 itibarıyla aylık paketiniz yenilenmiştir. Kalan kullanım hakkınızı https://nartelekom.com.tr/fatura adresinden veya uygullamamızdan görebilirsiniz.
  KANITLAR:
    (yok)

### mesru_11
TÜR: mesru_islem
ÖRNEK 1: e-Hizmet Kapısı: 20.07.2026 tarihli başvurunuz sonuçlanmıştır. Sonucu görüntülemek için sisteme kendi şifrenizle giriş yapınız. Şifrenizi kimseyle paylaşmayınız.
  KANITLAR:
    (yok)
ÖRNEK 2: e-Hizmet Kapisi: 03.03.2026 tarihli basvurunuz sonuclanmistir. Sonucu goruntulemek icin sisteme kendi sifrenizle giris yapiniz. Sifrenizi kimseyle paylasmayiniz.
  KANITLAR:
    (yok)

### mesru_12
TÜR: mesru_islem
ÖRNEK 1: Çarşıla: 355,99 lira tutarındaki iadeniz kartınıza aktarılmıştır. Bankanıza bağlı olarak hesabınıza yansıması birkaç iş günü sürebilir.
  KANITLAR:
    (yok)
ÖRNEK 2: Sepetgo: 4.990 TL tutarindaki iadeniz kartiniza aktarilmistir. Bankaniza bagli olarak hesabiniza yansimasi birkac is gunu surebilir.
  KANITLAR:
    (yok)

### mesru_13
TÜR: mesru_islem
ÖRNEK 1: Kuzeykart 08.04.2026 hesap kesim tarihli ekstre borcunuz 3.571 TL, asgari ödeme tutarı 28,99 TL. Son ödeme tarihi 18.06.2026. Otomatik ödeme talimatınız varsa işlem yapmanıza gerek yoktur.
  KANITLAR:
    (yok)
ÖRNEK 2: Kuzeykart 06.07.2026 hesap kesim tarihli ekstre borcunuz 2.212 TL, asgari odeme tutari 28,00 TL. Son odeme tarihi 15.01.2026. Otomatik odeme talimatiniz varsa islem yapmaniza gerek yoktur.
  KANITLAR:
    (yok)

### mesru_14
TÜR: mesru_islem
ÖRNEK 1: Serçe Lojistik: KG770349745 numaralı gönderiniz 22.07.2026 08:00 tarihinde teslim edilmiştir. Hizmetimizi değerlendirmek için: www.sercelojistik.com.tr/takip
  KANITLAR:
    (yok)
ÖRNEK 2: Serce Lojistik: HK653774909 numarali gonderiniz 01.11.2026 17:00 tarihinde teslim edilmistir. Hizmetimizi degerlendirmek icin: www.sercelojistik.com.tr/kampanya
  KANITLAR:
    (yok)

### odul_08
TÜR: odul_kampanya
ÖRNEK 1: Ardıçbank müşterisi olduğunuz için 3.372 TL hoş geldin bonusu kazandınız. Bonusu almak için internet şubesi bilgilerinizle giriş yapın www.eardicbank.xyz
  KANITLAR:
    - odul_vaadi: "3.372 TL hoş geldin bonusu kazandınız"
    - kimlik_talebi: "Bonusu almak için internet şubesi bilgilerinizle giriş yapın"
    - link: "www.eardicbank.xyz"
ÖRNEK 2: ARDIÇBANK MÜŞTERİSİ  OLDUĞUNUZ İÇİN 1.762₺  HOŞ  GELDİN BONUSU KAZANDINIZ.  BONUSU  ALMAK İÇİN İNTERNET ŞUBESİ BİLGİLERİNİZLE GİRİŞ  YAPIN HTTP://ARDİCBANKONLİNE.SBS/DOGRULA
  KANITLAR:
    - odul_vaadi: "1.762₺  HOŞ  GELDİN BONUSU KAZANDINIZ"
    - kimlik_talebi: "BONUSU  ALMAK İÇİN İNTERNET ŞUBESİ BİLGİLERİNİZLE GİRİŞ  YAPIN"
    - link: "HTTP://ARDİCBANKONLİNE.SBS/DOGRULA"

### odul_09
TÜR: odul_kampanya
ÖRNEK 1: Doğum gününüz kutlu olsun! 🎂 Nar Telekom size 3.426 TL hediye bakiye tanımladı. Hediyenizi 48 saat içinde alın rebrand.ly/XcyjLxST
  KANITLAR:
    - odul_vaadi: "size 3.426 TL hediye bakiye tanımladı"
    - link: "Hediyenizi 48 saat içinde alın rebrand.ly/XcyjLxST"
ÖRNEK 2: Doğum gününz kutlu olsun! 🎂 Nar Telekom size 3.109,00 TL hediye bakiye tanımladı. Hediyenizi 12 saat iinde alın https://t.co/MJjCwvi
  KANITLAR:
    - odul_vaadi: "size 3.109,00 TL hediye bakiye tanımladı"
    - link: "Hediyenizi 12 saat iinde alın https://t.co/MJjCwvi"

### odul_10
TÜR: odul_kampanya
ÖRNEK 1: Ahmet Bey, Çarşıla çekiliş sonuçları açıklandı: kahve makinesi kazananlar arasındasınız! Noter onay bedeli 43,90 TL https://casrila.buzz/9936
  KANITLAR:
    - odul_vaadi: "kahve makinesi kazananlar arasındasınız"
    - odeme_talebi: "Noter onay bedeli 43,90 TL"
    - link: "https://casrila.buzz/9936"
ÖRNEK 2: Selin Hanim, Sepetgo cekilis sonuclari aciklandi: kahve makinesi kazananlar arasindasiniz! Noter onay bedeli 63,49 TL http://sepetgogiris.net/giris
  KANITLAR:
    - odul_vaadi: "kahve makinesi kazananlar arasindasiniz"
    - odeme_talebi: "Noter onay bedeli 63,49 TL"
    - link: "http://sepetgogiris.net/giris"

### odul_11
TÜR: odul_kampanya
ÖRNEK 1: TEBRİKLER! Çarşıla 1.197 TL hediye kartı sizi bekliyor t.ly/6pE1ZkQj
  KANITLAR:
    - odul_vaadi: "Çarşıla 1.197 TL hediye kartı sizi bekliyor"
    - link: "t.ly/6pE1ZkQj"
ÖRNEK 2: TEBRIKLER! Sepetgo 3.323,99 TL hediye karti sizi bekliyor https://t.co/8z76w4b
  KANITLAR:
    - odul_vaadi: "Sepetgo 3.323,99 TL hediye karti sizi bekliyor"
    - link: "https://t.co/8z76w4b"

### odul_12
TÜR: odul_kampanya
ÖRNEK 1: Yonca Kart: Yıl sonu harcama ödülünüz 4.543 lira hesabınıza aktarılmayı bekliyor. Aktarım için doğum tarihinizi ve kart şifrenizi girin 48 saat içinde onaylayın
  KANITLAR:
    - odul_vaadi: "Yıl sonu harcama ödülünüz 4.543 lira"
    - kimlik_talebi: "Aktarım için doğum tarihinizi ve kart şifrenizi girin"
    - aciliyet: "48 saat içinde onaylayın"
ÖRNEK 2: Kuzeykart:  Yil sonu harcama odulunuz  1.991,50  TL  hesabiniza aktarilmayi bekliyor. Aktarim  icin  dogum tarihinizi ve kart sifrenizi girin 3 gun icinde onaylayin
  KANITLAR:
    - odul_vaadi: "Yil sonu harcama odulunuz  1.991,50  TL"
    - kimlik_talebi: "Aktarim  icin  dogum tarihinizi ve kart sifrenizi girin"
    - aciliyet: "3 gun icinde onaylayin"

### odul_13
TÜR: odul_kampanya
ÖRNEK 1: Turkuaz Mobil sürpriz kampanyası: numaranız 65.381 TL para ödülü kazandı! Ödülünüzü almak için [TEL] numarasını arayın, teslim için 105,99 TL işlem ücreti alınır.
  KANITLAR:
    - odul_vaadi: "numaranız 65.381 TL para ödülü kazandı"
    - kanal_degistirme: "Ödülünüzü almak için [TEL] numarasını arayın"
    - odeme_talebi: "teslim için 105,99 TL işlem ücreti"
ÖRNEK 2: TURKUAZ MOBİL SÜRPRİZ KAMPANYASI: NUMARANIZ 65.159 TL PARA ÖDÜLÜ KAZANDI! ÖDÜLÜNÜZÜ ALMAK İÇİN [TEL] NUMARASINI ARAYIN, TESLİM İÇİN 39,49 TL İŞLEM ÜCRETİ ALINIR.
  KANITLAR:
    - odul_vaadi: "NUMARANIZ 65.159 TL PARA ÖDÜLÜ KAZANDI"
    - kanal_degistirme: "ÖDÜLÜNÜZÜ ALMAK İÇİN [TEL] NUMARASINI ARAYIN"
    - odeme_talebi: "TESLİM İÇİN 39,49 TL İŞLEM ÜCRETİ"

### odul_14
TÜR: odul_kampanya
ÖRNEK 1: Lodos Mobil 10. yıl hediyesi: hattınıza 2.649,49₺ değerinde ücretsiz paket tanımlanacak. Tanımlama için abone şifrenizi girin https://cutt.ly/b2emrV
  KANITLAR:
    - odul_vaadi: "hattınıza 2.649,49₺ değerinde ücretsiz paket"
    - kimlik_talebi: "Tanımlama için abone şifrenizi girin"
    - link: "https://cutt.ly/b2emrV"
ÖRNEK 2: Lodos Mobil 10. yil hediyesi: hattiniza 2.773 lira degerinde ucretsiz paket tanimlanacak. Tanimlama icin abone sifrenizi girin cutt.ly/3FIlG
  KANITLAR:
    - odul_vaadi: "hattiniza 2.773 lira degerinde ucretsiz paket"
    - kimlik_talebi: "Tanimlama icin abone sifrenizi girin"
    - link: "cutt.ly/3FIlG"

### oyun_08
TÜR: oyun_hesap_skin
ÖRNEK 1: Kaleoyun ekibinden: beta testine seçildin, özel karakter kostümü hediye. Kayıt için kullanıcı adını ve şifreni forma yaz https://kaleoyun-tr.rest/odeme
  KANITLAR:
    - odul_vaadi: "beta testine seçildin, özel karakter kostümü hediye"
    - kimlik_talebi: "Kayıt için kullanıcı adını ve şifreni forma yaz"
    - link: "https://kaleoyun-tr.rest/odeme"
ÖRNEK 2: Kaleoyun ekibinden: beta testine  seçildin, özel karakter kostümü hediye. Kayıt için kullanıcı adını ve şifreni  forma yaz  https://ekaleoyun.net/8641
  KANITLAR:
    - odul_vaadi: "beta testine  seçildin, özel karakter kostümü hediye"
    - kimlik_talebi: "Kayıt için kullanıcı adını ve şifreni  forma yaz"
    - link: "https://ekaleoyun.net/8641"

### oyun_09
TÜR: oyun_hesap_skin
ÖRNEK 1: kanka Vaporia hesabımı satıyorum 1.265 TL'ye full skinli hesap, ödeme IBAN'a, detay için [TEL] destek ekibine yazma kapatırlar
  KANITLAR:
    - odeme_talebi: "1.265 TL'ye full skinli hesap"
    - kanal_degistirme: "ödeme IBAN'a, detay için [TEL]"
    - gizlilik_baskisi: "destek ekibine yazma kapatırlar"
ÖRNEK 2: kanka Kaleoyun hesabımı satıyorum 402 TL'ye full skinli  hesap,  ödeme IBAN'a, detay için  [TEL] destek  ekibine yazma kapatırlar
  KANITLAR:
    - odeme_talebi: "402 TL'ye full skinli  hesap"
    - kanal_degistirme: "ödeme IBAN'a, detay için  [TEL]"
    - gizlilik_baskisi: "destek  ekibine yazma kapatırlar"

### oyun_10
TÜR: oyun_hesap_skin
ÖRNEK 1: Vaporia Güvenlik: hesabınıza başka cihazdan girildi, şifrenizi bu sayfada sıfırlayın https://bit.ly/2VG88M 3 gün içinde envanteriniz kilitlenecek
  KANITLAR:
    - kimlik_talebi: "hesabınıza başka cihazdan girildi, şifrenizi bu sayfada sıfırlayın"
    - link: "https://bit.ly/2VG88M"
    - aciliyet: "3 gün içinde envanteriniz kilitlenecek"
ÖRNEK 2: Kaleoyun  Güvenlik: hesabınıza  başka cihazdan girildi, şifrenzi  bu sayfada sıfırlayın t.ly/nZ9oS 3 gün içinde envanteiniz kilitlenecek
  KANITLAR:
    - kimlik_talebi: "hesabınıza  başka cihazdan girildi, şifrenzi  bu sayfada sıfırlayın"
    - link: "t.ly/nZ9oS"
    - aciliyet: "3 gün içinde envanteiniz kilitlenecek"

### oyun_11
TÜR: oyun_hesap_skin
ÖRNEK 1: Bedava oyun parası! 💎 Kaleoyun jeneratörüyle sınırsız elmas www.kaleoyun-iade.buzz/tr/islem hesabına yüklemek için gelen doğrulama kodunu siteye gir
  KANITLAR:
    - odul_vaadi: "Kaleoyun jeneratörüyle sınırsız elmas"
    - link: "www.kaleoyun-iade.buzz/tr/islem"
    - kod_talebi: "hesabına yüklemek için gelen doğrulama kodunu siteye gir"
ÖRNEK 2: Bedava oyun parasi! 💎 Vaporia jeneratoruyle sinirsiz elmas www.vpaoria.rest/4682 hesabina yuklemek icin gelen dogrulama kodunu siteye gir
  KANITLAR:
    - odul_vaadi: "Vaporia jeneratoruyle sinirsiz elmas"
    - link: "www.vpaoria.rest/4682"
    - kod_talebi: "hesabina yuklemek icin gelen dogrulama kodunu siteye gir"

### oyun_12
TÜR: oyun_hesap_skin
ÖRNEK 1: Merhaba, ben Vaporia turnuva yöneticisi. Takımınız 34.660₺ ödüllü turnuvaya katılmaya hak kazandı. Kayıt ücreti kişi başı 26,90 TL, Discord'dan yazın Ayşe#7968
  KANITLAR:
    - odul_vaadi: "Takımınız 34.660₺ ödüllü turnuvaya katılmaya hak kazandı"
    - odeme_talebi: "Kayıt ücreti kişi başı 26,90 TL"
    - kanal_degistirme: "Discord'dan yazın Ayşe#7968"
ÖRNEK 2: Merhaba, ben Kaleoyun turnuva yoneticisi. Takiminiz 32.653 TL odullu turnuvaya katilmaya hak kazandi. Kayit ucreti kisi basi 70,90 lira, Discord'dan yazin Can#844574
  KANITLAR:
    - odul_vaadi: "Takiminiz 32.653 TL odullu turnuvaya katilmaya hak kazandi"
    - odeme_talebi: "Kayit ucreti kisi basi 70,90 lira"
    - kanal_degistirme: "Discord'dan yazin Can#844574"

### oyun_13
TÜR: oyun_hesap_skin
ÖRNEK 1: Seni hediye çekilişimize ekledim 🎁 3 kişiye 3.453,99 TL değerinde oyun kartı katılmak için Vaporia e-posta adresini ve şifreni DM at
  KANITLAR:
    - odul_vaadi: "3 kişiye 3.453,99 TL değerinde oyun kartı"
    - kimlik_talebi: "katılmak için Vaporia e-posta adresini ve şifreni DM at"
ÖRNEK 2: SENI HEDIEY CEKILISIMIZE EKLEDIM 🎁 3 KISIYE 2.805 TL DEGERINDE OYUN KRATI KATILMAK ICIN KALEOYUN E-POSTA ADRESINI VE SIFRENI DM AT
  KANITLAR:
    - odul_vaadi: "3 KISIYE 2.805 TL DEGERINDE OYUN KRATI"
    - kimlik_talebi: "KATILMAK ICIN KALEOYUN E-POSTA ADRESINI VE SIFRENI DM AT"

### oyun_14
TÜR: oyun_hesap_skin
ÖRNEK 1: Arenahub moderatörüyüm, hesabın hile kullanımı nedeniyle incelemede. Doğrulama için e-postana gelen kodu bana gönder yoksa 30 dakika içinde ban yersin
  KANITLAR:
    - yetki_iddiasi: "hesabın hile kullanımı nedeniyle incelemede"
    - kod_talebi: "Doğrulama için e-postana gelen kodu bana gönder"
    - aciliyet: "yoksa 30 dakika içinde ban yersin"
ÖRNEK 2: Arenahub moderatoruyum, hesabn hile kullanimi nedeniyle incelemede. Dogrulama icin e-postana gelen kodu bana gonder yoksa 2 saat icinde ban yersin
  KANITLAR:
    - yetki_iddiasi: "hesabn hile kullanimi nedeniyle incelemede"
    - kod_talebi: "Dogrulama icin e-postana gelen kodu bana gonder"
    - aciliyet: "yoksa 2 saat icinde ban yersin"

### reklam_08
TÜR: reklam_spam
ÖRNEK 1: Sepetgo'da 07.03.2026 tarihine kadar seçili ürünlerde kargo bedava! Hemen alışverişe başla: https://sepetgo.com.tr/fatura Ret: 3434
  KANITLAR:
    (yok)
ÖRNEK 2: Sepetgo'da 09.04.2026 tarihine kadar secili urunlerde kargo bedava! Hemen alisverise basla: https://sepetgo.com.tr/takip Ret: 4848
  KANITLAR:
    (yok)

### reklam_09
TÜR: reklam_spam
ÖRNEK 1: Mavibank'tan ihtiyaç kredisinde ay sonuna özel düşük faiz fırsatı! Başvuru: www.mavibank.com.tr/kampanya Ret için RET yazıp 7000'e gönderin. Mersis: 0430866939740048
  KANITLAR:
    (yok)
ÖRNEK 2: Ardicbank'tan ihtiyac kredisinde ay sonuna ozel dusuk faiz firsati! Basvuru: ardicbank.com.tr Ret icin RET yazip 4848'e gonderin. Mersis: 0176552723179194
  KANITLAR:
    (yok)

### reklam_10
TÜR: reklam_spam
ÖRNEK 1: Çarşıla'ya özel indirim kodun: HOSGELDIN 🎁 Sepette %30 indirim, 2 saat geçerli. https://carsila.com.tr/kampanya İYS ile ret: 7000
  KANITLAR:
    (yok)
ÖRNEK 2: CARSILA'YA OZEL INDIRIM KODUN: HOSGELDIN 🎁 SEPETTE %15 INDIRIM, 3 GUN GECERLI. WWW.CARSILA.COM.TR/FATURA IYS ILE RET: 4848
  KANITLAR:
    (yok)

### reklam_11
TÜR: reklam_spam
ÖRNEK 1: Nar Telekom: Bu hafta sonu tüm mağazalarımızda telefon alana kılıf ve ekran koruyucu hediye. Mağaza listesi uygulamamızda. SMS almamak için IPTAL yazıp 4848'e gönderin.
  KANITLAR:
    (yok)
ÖRNEK 2: Turkuaz Mobil: Bu hafta sonu tum magazalarimizda telefon alana kilif ve ekran koruyucu hediye. Magaza listesi uygulamamizda. SMS almamak icin IPTAL yazip 7000'e gonderin.
  KANITLAR:
    (yok)

### reklam_12
TÜR: reklam_spam
ÖRNEK 1: Kuzeykart'tan restoran harcamalarınıza 3 taksit fırsatı ve 143,50 TL'ye varan hediye puan! Detaylar: https://kuzeykart.com.tr/fatura Ret için 3434
  KANITLAR:
    (yok)
ÖRNEK 2: Yoncca Kart'tan restoran harcamalarınıza 3 taksit fırsatı ve 36,90 TL'ye varan hediye puan! Detaylar: https://yoncakart.com.tr/takip Ret için 2525
  KANITLAR:
    (yok)

### reklam_13
TÜR: reklam_spam
ÖRNEK 1: Çarşıla uygulamasında bu akşama özel yemek siparişlerinde %50 indirim 🍕 https://carsila.com.tr İletişim izni iptali: 3434
  KANITLAR:
    (yok)
ÖRNEK 2: Carsila uygulamasinda bu aksama ozel yemek siparislerinde %40 indirim 🍕 carsila.com.tr/kampanya Iletisim izni iptali: 4848
  KANITLAR:
    (yok)

### reklam_14
TÜR: reklam_spam
ÖRNEK 1: Pusula Kart sahiplerine sinema biletinde 1 alana 1 bedava! Kampanya 08.04.2026 tarihine kadar geçerlidir. Detay: www.pusulakart.com.tr/kampanya Ret için RET yazıp 7000'e gönderin.
  KANITLAR:
    (yok)
ÖRNEK 2: Pusula Kart sahiplerine  sinema biletinde  1 alana  1 bedava! Kampanya 20.08.2026  tarihine  kadar  geçerlidir. Detay: pusulakart.com.tr/kampanya Ret için RET yazıp 2525'e  gönderin.
  KANITLAR:
    (yok)

### yakin_08
TÜR: yakin_taklidi
ÖRNEK 1: Babacım ben, okulda telefonum çalındı 😢 eve dönmek için 89,50 TL lazım bu hesaba atar mısın [IBAN] lütfen hemen
  KANITLAR:
    - yakinlik_iddiasi: "Babacım ben, okulda telefonum çalındı"
    - odeme_talebi: "eve dönmek için 89,50 TL lazım bu hesaba atar mısın [IBAN]"
    - aciliyet: "lütfen hemen"
ÖRNEK 2: Anne ben, okudla telefonum calindi 😢 eve donmek icin 123,99₺ lazim bu hesaba atar misin [IBAN] lutfen hemen
  KANITLAR:
    - yakinlik_iddiasi: "Anne ben, okudla telefonum calindi"
    - odeme_talebi: "eve donmek icin 123,99₺ lazim bu hesaba atar misin [IBAN]"
    - aciliyet: "lutfen hemen"

### yakin_09
TÜR: yakin_taklidi
ÖRNEK 1: kanka ben Fatma, eski hattım kapandı bu numaradan yazıyorum. maaş yatana kadar 3.273,00 lira borç verebilir misin IBAN [IBAN]
  KANITLAR:
    - yakinlik_iddiasi: "kanka ben Fatma, eski hattım kapandı bu numaradan yazıyorum"
    - odeme_talebi: "maaş yatana kadar 3.273,00 lira borç verebilir misin"
ÖRNEK 2: !!️ kanka ben Umit, eski hattim kapandi bu numaradan yaziyorum. maas yatana kadar 4.151 TL borc verebilir misin IBAN [IBAN]
  KANITLAR:
    - yakinlik_iddiasi: "kanka ben Umit, eski hattim kapandi bu numaradan yaziyorum"
    - odeme_talebi: "maas yatana kadar 4.151 TL borc verebilir misin"

### yakin_10
TÜR: yakin_taklidi
ÖRNEK 1: Abla sesli mesaj atamıyorum mikrofon bozuk bu benim yeni hattım kredi kartı borcum için 1.348,99 TL lazım yarın iade ederim
  KANITLAR:
    - yakinlik_iddiasi: "bu benim yeni hattım"
    - odeme_talebi: "kredi kartı borcum için 1.348,99 TL lazım yarın iade ederim"
ÖRNEK 2: ⚠️ Dayı sesli mesaj  atamıyorum mikrofon bozuk bu benim  yeni hattım  kredi kartı borcum için  826,49  lira lazım yarın iade ederim
  KANITLAR:
    - yakinlik_iddiasi: "bu benim  yeni hattım"
    - odeme_talebi: "kredi kartı borcum için  826,49  lira lazım yarın iade ederim"

### yakin_11
TÜR: yakin_taklidi
ÖRNEK 1: Merhaba Anne ben, numaramı değiştirdim. Bana 4.986 TL değerinde dijital hediye kartı alıp kodunu atar mısın akşama kadar lazım
  KANITLAR:
    - yakinlik_iddiasi: "Anne ben, numaramı değiştirdim"
    - odeme_talebi: "Bana 4.986 TL değerinde dijital hediye kartı alıp kodunu atar mısın"
    - aciliyet: "akşama kadar lazım"
ÖRNEK 2: Merhabba Babacım ben, numaramı değiştirdim. Bana 4.963 TL değerinde dijital hediye kartı alıp koudnu atar mısın akşama kadar lazzım
  KANITLAR:
    - yakinlik_iddiasi: "Babacım ben, numaramı değiştirdim"
    - odeme_talebi: "Bana 4.963 TL değerinde dijital hediye kartı alıp koudnu atar mısın"
    - aciliyet: "akşama kadar lazzım"

### yakin_12
TÜR: yakin_taklidi
ÖRNEK 1: Anne ben, küçük bir kaza yaptım karakoldayım. Avukat için 25.397 TL göndermen lazım kimseye haber verme, rezil olurum
  KANITLAR:
    - yakinlik_iddiasi: "Anne ben, küçük bir kaza yaptım karakoldayım"
    - odeme_talebi: "Avukat için 25.397 TL göndermen lazım"
    - gizlilik_baskisi: "kimseye haber verme, rezil olurum"
ÖRNEK 2: Kardesim ben, kuuck  bir kaza yaptim karakoldayim.  Avukat icin 12.845₺ gondermen lazim  kimseye haber verme,  reil  olurum
  KANITLAR:
    - yakinlik_iddiasi: "Kardesim ben, kuuck  bir kaza yaptim karakoldayim"
    - odeme_talebi: "Avukat icin 12.845₺ gondermen lazim"
    - gizlilik_baskisi: "kimseye haber verme,  reil  olurum"

### yakin_13
TÜR: yakin_taklidi
ÖRNEK 1: Abla benim, yeni telefon aldım uygulamaya kart eklerken sorun çıktı. Senin kartının önlü arkalı fotoğrafını atar mısın şimdi lazım
  KANITLAR:
    - yakinlik_iddiasi: "Abla benim, yeni telefon aldım"
    - kimlik_talebi: "Senin kartının önlü arkalı fotoğrafını atar mısın"
    - aciliyet: "şimdi lazım"
ÖRNEK 2: Teyze benim, yeni telefon aldım uygulamaya kart eklerkne sorun çıktı. Snin kartının önlü arkalı fotoğrafını atar mısın şimdi lazım
  KANITLAR:
    - yakinlik_iddiasi: "Teyze benim, yeni telefon aldım"
    - kimlik_talebi: "Snin kartının önlü arkalı fotoğrafını atar mısın"
    - aciliyet: "şimdi lazım"

### yakin_14
TÜR: yakin_taklidi
ÖRNEK 1: Abi benim bu, eski hattım kapandı yeni numaram bu. Okul taksidi için 3.388 TL [IBAN] hesabına yatırır mısın, kimse bilmesin şimdilik.
  KANITLAR:
    - yakinlik_iddiasi: "benim bu, eski hattım kapandı yeni numaram bu"
    - odeme_talebi: "Okul taksidi için 3.388 TL [IBAN] hesabına yatırır mısın"
    - gizlilik_baskisi: "kimse bilmesin şimdilik"
ÖRNEK 2: Kanka benim bu, eski hattim kapandi yeni numaram bu. Okul taksidi icin 477 lira [IBAN] hesabina yatirir misin, kimse bilmesin simdilik.
  KANITLAR:
    - yakinlik_iddiasi: "benim bu, eski hattim kapandi yeni numaram bu"
    - odeme_talebi: "Okul taksidi icin 477 lira [IBAN] hesabina yatirir misin"
    - gizlilik_baskisi: "kimse bilmesin simdilik"

### yatirim_08
TÜR: yatirim_vip_grup
ÖRNEK 1: 📈 Boğaz Yatırım Kripto Sinyal: dün paylaştığımız coin %500 yükseldi! Yeni sinyaller için grubumuza katılın https://t.me/bogazyatirimvip
  KANITLAR:
    - odul_vaadi: "dün paylaştığımız coin %500 yükseldi"
    - kanal_degistirme: "Yeni sinyaller için grubumuza katılın https://t.me/bogazyatirimvip"
ÖRNEK 2: 📈  Boğaz Yatırım Kripto Sinyal: dün paylaştığımız coin %500 yükseldi!  Yeni  sinyaller için  grubumuza katılın chat.whatsapp.com/ipoXSYD29X
  KANITLAR:
    - odul_vaadi: "dün paylaştığımız coin %500 yükseldi"
    - kanal_degistirme: "Yeni  sinyaller için  grubumuza katılın chat.whatsapp.com/ipoXSYD29X"

### yatirim_09
TÜR: yatirim_vip_grup
ÖRNEK 1: Selin Hanım merhaba, ben Boğaz Yatırım portföy yöneticisi. Halka arz öncesi hisseden size özel pay ayırdık. Rezervasyon için 2.609 TL kaparo yeterli. Bugün kapanıyor
  KANITLAR:
    - odul_vaadi: "Halka arz öncesi hisseden size özel pay ayırdık"
    - odeme_talebi: "Rezervasyon için 2.609 TL kaparo yeterli"
    - aciliyet: "Bugün kapanıyor"
ÖRNEK 2: ⚠️ Çağla Hanım merhaba, ben Boğaz Yatırım portföy yöneticisi. Halka arz öncesi hisseden size özel pay ayırdık. Rezervasyon için 2.929 TL kaparo yeterli. Bugün kapanıyor
  KANITLAR:
    - odul_vaadi: "Halka arz öncesi hisseden size özel pay ayırdık"
    - odeme_talebi: "Rezervasyon için 2.929 TL kaparo yeterli"
    - aciliyet: "Bugün kapanıyor"

### yatirim_10
TÜR: yatirim_vip_grup
ÖRNEK 1: Ünlü bir iş insanının açıkladığı yöntemle 4.902,99 TL ile başlayıp ayda 94.839 TL kazanın. Videoyu izleyin ve kaydolun: www.bogazyatirim-guvenlik.info/1166
  KANITLAR:
    - odul_vaadi: "4.902,99 TL ile başlayıp ayda 94.839 TL kazanın"
    - link: "Videoyu izleyin ve kaydolun: www.bogazyatirim-guvenlik.info/1166"
ÖRNEK 2: Unlu bir is insaninin acikladigi yontemle 3.998 TL ile baslayip ayda 44.041 TL kazanin. Videoyu izleyin ve kaydolun: https://bogazyatirimgiris.rest/tr/islem
  KANITLAR:
    - odul_vaadi: "3.998 TL ile baslayip ayda 44.041 TL kazanin"
    - link: "Videoyu izleyin ve kaydolun: https://bogazyatirimgiris.rest/tr/islem"

### yatirim_11
TÜR: yatirim_vip_grup
ÖRNEK 1: Boğaz Yatırım: Hesabınız yükseltilmeye uygun. Gold üyelikte günlük %50 getiri. Yükseltme için 2.521 lira yatırım yapın, IBAN: [IBAN]
  KANITLAR:
    - odul_vaadi: "Gold üyelikte günlük %50 getiri"
    - odeme_talebi: "Yükseltme için 2.521 lira yatırım yapın"
ÖRNEK 2: Boğaz Yatırım: Hesabınız yükseltilmeye uygun. Gold üyelikte günlük %20 getiri. Yükseltme için 4.394,50 TL yatırım yapın, IBAN: [IBAN]
  KANITLAR:
    - odul_vaadi: "Gold üyelikte günlük %20 getiri"
    - odeme_talebi: "Yükseltme için 4.394,50 TL yatırım yapın"

### yatirim_12
TÜR: yatirim_vip_grup
ÖRNEK 1: Selam, ben de önce inanmamıştım ama Boğaz Yatırım grubundaki hocanın önerileriyle bu ay 72.575₺ kazandım. İstersen seni de gruba ekleteyim chat.whatsapp.com/jFDFnmkX5j
  KANITLAR:
    - odul_vaadi: "bu ay 72.575₺ kazandım"
    - kanal_degistirme: "İstersen seni de gruba ekleteyim chat.whatsapp.com/jFDFnmkX5j"
ÖRNEK 2: Selam, ben de once inanmamistim ama Bogaz Yatirim grubundaki hocanin onerileriyle bu ay 7.115 TL kazandim. Istersen seni de gruba ekleteyim chat.whatsapp.com/zuAWRJk2AH
  KANITLAR:
    - odul_vaadi: "bu ay 7.115 TL kazandim"
    - kanal_degistirme: "Istersen seni de gruba ekleteyim chat.whatsapp.com/zuAWRJk2AH"

### yatirim_13
TÜR: yatirim_vip_grup
ÖRNEK 1: Boğaz Yatırım uluslararası fon: devlet güvenceli altın fonuyla yıllık %70 getiri. Ücretsiz ön görüşme için uygulamayı indirin http://bogazyatirim-iade.monster/tr/islem Kampanya 13.01.2026 tarihinde sona eriyor
  KANITLAR:
    - odul_vaadi: "devlet güvenceli altın fonuyla yıllık %70 getiri"
    - kanal_degistirme: "Ücretsiz ön görüşme için uygulamayı indirin"
    - aciliyet: "Kampanya 13.01.2026 tarihinde sona eriyor"
ÖRNEK 2: Boğaz Yatırım  uluslararası  fon: devlet güvenceli  altın fonuyla yılılk %500 getiri. Ücretsiz ön görüşme için uyuglamayı indirin https://bogazyatirimonline.site/tr/islem Kampanya  11.01.2026 tarihinde sona eriyor
  KANITLAR:
    - odul_vaadi: "devlet güvenceli  altın fonuyla yılılk %500 getiri"
    - kanal_degistirme: "Ücretsiz ön görüşme için uyuglamayı indirin"
    - aciliyet: "Kampanya  11.01.2026 tarihinde sona eriyor"

### yatirim_14
TÜR: yatirim_vip_grup
ÖRNEK 1: Arkadaşlar Kule Menkul kanalında yarın patlayacak hisseyi paylaştık 🚀 Premium üyelik 2.916₺, ödeme dekontunu [TEL] numarasına atın
  KANITLAR:
    - odul_vaadi: "yarın patlayacak hisseyi"
    - odeme_talebi: "Premium üyelik 2.916₺"
    - kanal_degistirme: "ödeme dekontunu [TEL] numarasına atın"
ÖRNEK 2: Arkadalsar Kule Menkul kanalinda yarin patlayacak hisseyi paylastik 🚀 Premium uyyelik 3.829,00 TL, odeme dekontunu [TEL] numarasina atin
  KANITLAR:
    - odul_vaadi: "yarin patlayacak hisseyi"
    - odeme_talebi: "Premium uyyelik 3.829,00 TL"
    - kanal_degistirme: "odeme dekontunu [TEL] numarasina atin"
