# Görev: Türkçe dolandırıcılık SMS veri setinin etiket denetimi

Sen bağımsız bir veri denetçisisin. Aşağıdaki 150 SENTETİK SMS mesajı bir başka model tarafından şablonlardan
üretildi ve etiketlendi. Görevin etiket hatalarını bulmak. Kurum adları ve numaralar uydurmadır.

## Her örnek için sırayla sor; "hayır" dediğin İLK soruda karar ver
1. Böyle bir SMS gerçek hayatta gelebilir mi? Anlamca çelişkili, saçma ya da okunamaz ise → "cikar"
2. Tür AÇIKÇA yanlış mı? → "tur" (+ yeni_tur)
3. Bir kanıt alıntısı yanındaki sinyalle AÇIKÇA uyuşmuyor mu, ya da mesajın ANA dolandırıcılık hamlesi
   kanıtlarda hiç yok mu? → "kanit"
4. Hiçbiri değilse → "dogru"

## Önemli kurallar
- Emin değilsen "dogru". İki tür de savunulabiliyorsa "dogru". Sadece AÇIK hataları işaretle.
- BİLİNÇLİ gürültü, hata DEĞİLDİR: Türkçe karaktersiz yazım, yazım hataları, çift boşluk, BÜYÜK HARF, emoji,
  uydurma marka adları, [TEL] [IBAN] [OTP] [KART] maske etiketleri.
- En fazla 3 kanıt seçilebilir; küçük ayrıntıların eksikliği hata değildir.
- reklam_spam ve mesru_islem için kanıt listesinin BOŞ olması doğrudur (kanıtlar yalnızca dolandırıcılık işaretleri içindir).
- Model risk seviyesi üretmez; risk değerlendirme.

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

## Çıktı biçimi (YALNIZCA geçerli bir JSON dizisi, başka metin yok; her örnek için tam bir öğe)
[{"id": "tes-00134", "karar": "dogru"},
 {"id": "tes-00166", "karar": "kanit", "not": "kısa gerekçe"},
 {"id": "tes-00074", "karar": "tur", "yeni_tur": "mesru_islem", "not": "kısa gerekçe"},
 {"id": "tes-00012", "karar": "cikar", "not": "kısa gerekçe"}]
"karar" ∈ dogru | tur | kanit | cikar. "dogru" dışındaki her kararda "not" zorunlu.

## Örnekler

### tes-oyun_06-003
MESAJ: Zirvearena: 2.793,49 TL  değerinde  cüzdan bakiyesi hediye!  Hesabını  bağla ve kodu onayla cutt.ly/ifhoxc
TÜR: oyun_hesap_skin
KANITLAR:
  - odul_vaadi: "2.793,49 TL  değerinde  cüzdan bakiyesi hediye"
  - kimlik_talebi: "Hesabını  bağla ve kodu onayla"
  - link: "cutt.ly/ifhoxc"

### tes-kamu_06-009
MESAJ: Il Emniyet Mudurlugu Mali Sube: Ilgaz Bank kartiniz yasa disi bahiste kullanilmis. Hesabinizin dondurulmamasi icin SMS ile gelen onay kodunu soyleyin, aramizda kalsin.
TÜR: sahte_kamu_gorevlisi
KANITLAR:
  - yetki_iddiasi: "Il Emniyet Mudurlugu Mali Sube: Ilgaz Bank kartiniz yasa disi bahiste"
  - kod_talebi: "Hesabinizin dondurulmamasi icin SMS ile gelen onay kodunu soyleyin"
  - gizlilik_baskisi: "aramizda kalsin"

### tes-mesru_06-000
MESAJ: Pazaryolu siparisiniz onaylandi. Siparis tutari 3.498  lira.  Tahmini teslim 09.07.2026. Giris kodunuz [OTP], kimseyle paylasmayiniz.
TÜR: mesru_islem
KANITLAR:
  (yok)

### tes-gorev_06-000
MESAJ: Pazaryolu mağaza puanlama görevi: 4.387 TL komisyon. Siparişi önce kendi hesabınızdan 1.218 TL ile verin, iade ediyoruz. Görevli: [TEL]
TÜR: gorev_is_ilani
KANITLAR:
  - odul_vaadi: "4.387 TL komisyon"
  - odeme_talebi: "Siparişi önce kendi hesabınızdan 1.218 TL ile verin"
  - kanal_degistirme: "Görevli: [TEL]"

### tes-reklam_06-001
MESAJ: Gökkuşağı Mobil fiber internette yeni yıl kampanyası: 12 ay boyunca 262₺. Hemen başvurun: https://gokkusagimobil.com.tr Ret için 3434
TÜR: reklam_spam
KANITLAR:
  (yok)

### tes-yakin_06-013
MESAJ: Dayı benim, yurt dışındayım kartım bloke oldu, otel için 2.856 lira lazım arkadaşın hesabına at [IBAN] çok acil lütfen
TÜR: yakin_taklidi
KANITLAR:
  - yakinlik_iddiasi: "Dayı benim, yurt dışındayım kartım bloke oldu"
  - odeme_talebi: "otel için 2.856 lira lazım arkadaşın hesabına at [IBAN]"
  - aciliyet: "çok acil lütfen"

### tes-bahis_06-009
MESAJ: Şike garantili maç listesi geldi, oranlar çok yüksek. Listeyi almak için 3.639 TL yatır [TEL] WhatsApp
TÜR: yasa_disi_bahis
KANITLAR:
  - odul_vaadi: "Şike garantili maç listesi"
  - odeme_talebi: "Listeyi almak için 3.639 TL yatır"
  - kanal_degistirme: "[TEL] WhatsApp"

### tes-yatirim_06-011
MESAJ: Yapay zeka destekli robot ile guluk 2.488,99₺ pasif gelir! Baslangic paketi sadece 342,50₺ Kait icin t.me/+n317WNLBHb
TÜR: yatirim_vip_grup
KANITLAR:
  - odul_vaadi: "Yapay zeka destekli robot ile guluk 2.488,99₺ pasif gelir"
  - odeme_talebi: "Baslangic paketi sadece 342,50₺"
  - kanal_degistirme: "Kait icin t.me/+n317WNLBHb"

### tes-yatirim_07-010
MESAJ: Liman Portfoy: Portfoyunuzde 81.035 TL kar biritki. Cekim icin once 1.072 lira komisyon odemniz gerekiyor. Bugun odmezseniz kariniz sifirlanir.
TÜR: yatirim_vip_grup
KANITLAR:
  - odul_vaadi: "81.035 TL kar biritki"
  - odeme_talebi: "Cekim icin once 1.072 lira komisyon odemniz gerekiyor"
  - aciliyet: "Bugun odmezseniz kariniz sifirlanir"

### tes-oyun_07-004
MESAJ: abi oyun içi parayı yarı fiyatına satıyorum 2.521 TL'ye 10.000 elmas, hesabına yüklemem için gelen kodu at moderatörlere söyleme banlarlar
TÜR: oyun_hesap_skin
KANITLAR:
  - odeme_talebi: "2.521 TL'ye 10.000 elmas"
  - kod_talebi: "hesabına yüklemem için gelen kodu at"
  - gizlilik_baskisi: "moderatörlere söyleme banlarlar"

### tes-kurum_06-007
MESAJ: Ilgaz Bank: mobil subeniz yeni cihazda acildi. Siz degilseniz hemen bilgilerinizi guncelleyin ilgazbankgiris.sbs/giris
TÜR: kurum_taklidi
KANITLAR:
  - kurum_taklidi: "Ilgaz Bank: mobil subeniz yeni cihazda acildi"
  - aciliyet: "hemen"
  - kimlik_talebi: "bilgilerinizi guncelleyin"

### tes-bahis_06-008
MESAJ: Şike garantili maç listesi geldi, oranlar çok yüksek. Listeyi almak için 2.512₺ yatır [TEL] WhatsApp
TÜR: yasa_disi_bahis
KANITLAR:
  - odul_vaadi: "Şike garantili maç listesi"
  - odeme_talebi: "Listeyi almak için 2.512₺ yatır"
  - kanal_degistirme: "[TEL] WhatsApp"

### tes-bahis_07-009
MESAJ: Adres guncellendi! tribunbet yeni domain: https://tribunbet726.win Uye ol 1.708 TL bedava bahis
TÜR: yasa_disi_bahis
KANITLAR:
  - link: "https://tribunbet726.win"
  - odul_vaadi: "Uye ol 1.708 TL bedava bahis"

### tes-oyun_07-010
MESAJ: abi  oyun  içi parayı yarı fiyatına satıyorum 4.756,50 TL'ye  10.000 elmas, hesabına yüklemem için gelen kodu at moderatörlere söyleme banlarlar
TÜR: oyun_hesap_skin
KANITLAR:
  - odeme_talebi: "4.756,50 TL'ye  10.000 elmas"
  - kod_talebi: "hesabına yüklemem için gelen kodu at"
  - gizlilik_baskisi: "moderatörlere söyleme banlarlar"

### tes-mesru_07-005
MESAJ: Kamu Portalı: 06.05.2026 günü saat 08:00 için hastane randevunuz oluşturulmuştur. İptal için randevu sistemini kullanınız.
TÜR: mesru_islem
KANITLAR:
  (yok)

### tes-mesru_07-008
MESAJ: Kamu Portalı: 03.08.2026 günü saat 09:15 için hastane randevunuz oluşturulmuştur. İptal için randevu sistemini kullanınız.
TÜR: mesru_islem
KANITLAR:
  (yok)

### tes-kurum_06-013
MESAJ: Ilgaz Bank: mobil şubeniz yeni cihazda açıldı. Siz değilseniz hemen bilgilerinizi güncelleyin https://ilgazbank-iade.live/dogrula
TÜR: kurum_taklidi
KANITLAR:
  - kurum_taklidi: "Ilgaz Bank: mobil şubeniz yeni cihazda açıldı"
  - aciliyet: "hemen"
  - kimlik_talebi: "bilgilerinizi güncelleyin"

### tes-odul_06-008
MESAJ: ⚠️ Sansli musterimiz secildiniz, iPhone sizin! Sadece 146,50 lira sigorta bedeli odeyin. Pazaryolu t.co/GRhLW
TÜR: odul_kampanya
KANITLAR:
  - odul_vaadi: "Sansli musterimiz secildiniz, iPhone sizin"
  - odeme_talebi: "Sadece 146,50 lira sigorta bedeli"
  - link: "t.co/GRhLW"

### tes-reklam_06-013
MESAJ: Gökkuşağı Mobil fiber internette yeni yıl kampanyası: 12 ay boyunca 2.135 TL. Hemen başvurun: gokkusagimobil.com.tr Ret için 7000
TÜR: reklam_spam
KANITLAR:
  (yok)

### tes-oyun_06-011
MESAJ: Zirvearena: 4.563 lira degerinde cuzdan bakiyesi hediye! Hesabini bagla ve  kodu  onayla  https://s.id/HoTnxr
TÜR: oyun_hesap_skin
KANITLAR:
  - odul_vaadi: "4.563 lira degerinde cuzdan bakiyesi hediye"
  - kimlik_talebi: "Hesabini bagla ve  kodu  onayla"
  - link: "https://s.id/HoTnxr"

### tes-reklam_07-008
MESAJ: Poyraz Kart sahiplerine akaryakıtta %10 indirim fırsatı 23.01.2026 tarihine kadar. Detaylar www.poyrazkart.com.tr/fatura adresinde. Ret için 3434'e RET yazın. Mersis: 0456796055428471
TÜR: reklam_spam
KANITLAR:
  (yok)

### tes-reklam_06-009
MESAJ: Gökkuşağı Mobil fiber internette yeni yıl kampanyası: 12 ay boyunca 4.982 TL. Hemen başvurun: gokkusagimobil.com.tr/fatura Ret için 7000
TÜR: reklam_spam
KANITLAR:
  (yok)

### tes-kamu_07-005
MESAJ: Sayın vatandaşımız, hakkınızda dolandırıcılık soruşturması başlatılmıştır. Dosya numaranız için [TEL] numaralı savcılık hattını arayın. 1 saat içinde aramazsanız gıyabınızda işlem yapılacaktır.
TÜR: sahte_kamu_gorevlisi
KANITLAR:
  - yetki_iddiasi: "hakkınızda dolandırıcılık soruşturması başlatılmıştır"
  - kanal_degistirme: "Dosya numaranız için [TEL] numaralı savcılık hattını arayın"
  - aciliyet: "1 saat içinde aramazsanız gıyabınızda işlem yapılacaktır"

### tes-oyun_07-003
MESAJ: abi oyun içi parayı yarı fiyatına satıyorum 3.845 TL'ye 10.000 elmas, hesabına yüklemem için gelen kodu at moderatörlere söyleme banlarlar
TÜR: oyun_hesap_skin
KANITLAR:
  - odeme_talebi: "3.845 TL'ye 10.000 elmas"
  - kod_talebi: "hesabına yüklemem için gelen kodu at"
  - gizlilik_baskisi: "moderatörlere söyleme banlarlar"

### tes-kurum_07-007
MESAJ: Pazaryolu hesabınızda olağandışı giriş tespit edildi. Hesabınızı korumak için şifrenizi yenileyin www.epazaryolu.cfd/giris 30 dakika içinde işlem yapılmazsa hesabınız silinir
TÜR: kurum_taklidi
KANITLAR:
  - kimlik_talebi: "Hesabınızı korumak için şifrenizi yenileyin"
  - link: "www.epazaryolu.cfd/giris"
  - aciliyet: "30 dakika içinde işlem yapılmazsa hesabınız silinir"

### tes-kargo_06-009
MESAJ: Merhaba, Turna Kargo şubesinde  adınıza kayıtlı bir  koli var. Teslim almak  için kart bilgilerinizi doğrulayın hxxp://turnakargo-guvenlik[.]site/odeme Hizmet  bedeli 128,00 TL
TÜR: sahte_kargo_gumruk
KANITLAR:
  - kimlik_talebi: "Teslim almak  için kart bilgilerinizi doğrulayın"
  - link: "hxxp://turnakargo-guvenlik[.]site/odeme"
  - odeme_talebi: "Hizmet  bedeli 128,00 TL"

### tes-yakin_06-011
MESAJ: Kardesim benim, yurt disindayim kartim bloke oldu, otel icin 1.495 TL lazim arkadasin hesabina at [IBAN] cok acil lutfen
TÜR: yakin_taklidi
KANITLAR:
  - yakinlik_iddiasi: "Kardesim benim, yurt disindayim kartim bloke oldu"
  - odeme_talebi: "otel icin 1.495 TL lazim arkadasin hesabina at [IBAN]"
  - aciliyet: "cok acil lutfen"

### tes-gorev_07-010
MESAJ: Is basvurunuz onaylandi! Haftaik 54.581 TL kazanc icin kargo ve paketleme kiti 4.316,49 lira Detaylar icin su numaraya yazin [TEL]
TÜR: gorev_is_ilani
KANITLAR:
  - odul_vaadi: "Haftaik 54.581 TL kazanc"
  - odeme_talebi: "kargo ve paketleme kiti 4.316,49 lira"
  - kanal_degistirme: "Detaylar icin su numaraya yazin [TEL]"

### tes-yakin_06-001
MESAJ: Kardeşim benim, yurt dışındayım kartım bloke oldu, otel için 3.554,49 TL lazım arkadaşın hesabına at [IBAN] çok acil lüften
TÜR: yakin_taklidi
KANITLAR:
  - yakinlik_iddiasi: "Kardeşim benim, yurt dışındayım kartım bloke oldu"
  - odeme_talebi: "otel için 3.554,49 TL lazım arkadaşın hesabına at [IBAN]"
  - aciliyet: "çok acil lüften"

### tes-gorev_07-009
MESAJ: İş başvurunuz onaylandı! Haftalık 5.291 TL kazanç için kargo ve paketleme kiti 2.004,50 TL Detaylar için şu numaaya yazın [TEL]
TÜR: gorev_is_ilani
KANITLAR:
  - odul_vaadi: "Haftalık 5.291 TL kazanç"
  - odeme_talebi: "kargo ve paketleme kiti 2.004,50 TL"
  - kanal_degistirme: "Detaylar için şu numaaya yazın [TEL]"

### tes-reklam_07-012
MESAJ: POYRAZ KART SAHİPLERİNE AKARYAKİTTA %50 İNDİRİM FİRSATİ 17.07.2026 TARİHİNE KADAR. DETAYLAR WWW.POYRAZKART.COM.TR ADRESİNDE. RET İCİN 3434'E RET YAZİN. MERSİS: 0795955582900330
TÜR: reklam_spam
KANITLAR:
  (yok)

### tes-bahis_06-002
MESAJ: Şike garantili maç listesi geldi, oranlar çok yüksek. Listeyi almak için 3.923,99 TL yatır [TEL] WhatsApp
TÜR: yasa_disi_bahis
KANITLAR:
  - odul_vaadi: "Şike garantili maç listesi"
  - odeme_talebi: "Listeyi almak için 3.923,99 TL yatır"
  - kanal_degistirme: "[TEL] WhatsApp"

### tes-oyun_07-007
MESAJ: abi oyun içi parayı yarı fiyatına satıyorum 2.690 TL'ye 10.000 elmas, hesabına yüklemem için gelen kodu at moderatörlere söyleme banlarlar
TÜR: oyun_hesap_skin
KANITLAR:
  - odeme_talebi: "2.690 TL'ye 10.000 elmas"
  - kod_talebi: "hesabına yüklemem için gelen kodu at"
  - gizlilik_baskisi: "moderatörlere söyleme banlarlar"

### tes-kurum_07-006
MESAJ: Pazaryolu hesabınızda olağandışı giriş tespit edildi. Hesabınızı korumak için şifrenizi yenileyin www.pazaryolu-guvenlik.win 2 saat içinde işlem yapılmazsa hesabınız silinir
TÜR: kurum_taklidi
KANITLAR:
  - kimlik_talebi: "Hesabınızı korumak için şifrenizi yenileyin"
  - link: "www.pazaryolu-guvenlik.win"
  - aciliyet: "2 saat içinde işlem yapılmazsa hesabınız silinir"

### tes-kamu_07-006
MESAJ: 📦 Sayın vatndaşımız, hakkınızda dolandırıcılık soruşturması başatılmıştır. Dosya numaranız için [TEL] numaralı savcılık hattını arayın. 24 saat içinde arramazsanız gıyabınızda işlem yapılacaktır.
TÜR: sahte_kamu_gorevlisi
KANITLAR:
  - yetki_iddiasi: "hakkınızda dolandırıcılık soruşturması başatılmıştır"
  - kanal_degistirme: "Dosya numaranız için [TEL] numaralı savcılık hattını arayın"
  - aciliyet: "24 saat içinde arramazsanız gıyabınızda işlem yapılacaktır"

### tes-yakin_06-004
MESAJ: Baba benim, yurt dışındayım kartım bloke oldu, otel için 1.879,90₺ lazım arkadaşın hesabına at [IBAN] çok acil lütfen
TÜR: yakin_taklidi
KANITLAR:
  - yakinlik_iddiasi: "Baba benim, yurt dışındayım kartım bloke oldu"
  - odeme_talebi: "otel için 1.879,90₺ lazım arkadaşın hesabına at [IBAN]"
  - aciliyet: "çok acil lütfen"

### tes-yatirim_07-001
MESAJ: Liman Portföy: Portföyünüzde 78.742 TL kâr birikti. Çekim için önce 2.857 TL komisyon ödemeniz gerekiyor. Bugün ödemezseniz kârınız sıfırlanır.
TÜR: yatirim_vip_grup
KANITLAR:
  - odul_vaadi: "78.742 TL kâr birikti"
  - odeme_talebi: "Çekim için önce 2.857 TL komisyon ödemeniz gerekiyor"
  - aciliyet: "Bugün ödemezseniz kârınız sıfırlanır"

### tes-gorev_06-001
MESAJ: 🎁 Pazaryolu mağaza puanlama görevi: 1.538 lira komisyon. Siparişi önce kendi hesabınızdan 325 TL ile verin, iade ediyoruz. Görevli: [TEL]
TÜR: gorev_is_ilani
KANITLAR:
  - odul_vaadi: "1.538 lira komisyon"
  - odeme_talebi: "Siparişi önce kendi hesabınızdan 325 TL ile verin"
  - kanal_degistirme: "Görevli: [TEL]"

### tes-reklam_06-004
MESAJ: Gökkuşağı Mobil fiber internette yeni yıl kampanyası: 12 ay boyunca 2.797₺. Hemen başvurun: www.gokkusagimobil.com.tr Ret için 4848
TÜR: reklam_spam
KANITLAR:
  (yok)

### tes-yakin_07-003
MESAJ: Dayi yeni numarami kaydet,  eskisi  kapandi. Kirami  yatiramadim 2.816₺ gonderir  misin aramizda kalsin
TÜR: yakin_taklidi
KANITLAR:
  - yakinlik_iddiasi: "Dayi yeni numarami kaydet,  eskisi  kapandi"
  - odeme_talebi: "Kirami  yatiramadim 2.816₺ gonderir  misin"
  - gizlilik_baskisi: "aramizda kalsin"

### tes-kamu_06-022
MESAJ: IL EMNİYET MUDURLUGU MALİ SUBE: SEDİRBANK KARTİNİZ YASA DİSİ BAHİSTE KULLANİLMİS. HESABİNİZİN DONDURULMAMASİ İCİN SMS İLE GELEN ONAY KODUNU SOYLEYİN, ARAMİZDA KALSİN.
TÜR: sahte_kamu_gorevlisi
KANITLAR:
  - yetki_iddiasi: "IL EMNİYET MUDURLUGU MALİ SUBE: SEDİRBANK KARTİNİZ YASA DİSİ BAHİSTE KULLANİLMİS"
  - kod_talebi: "HESABİNİZİN DONDURULMAMASİ İCİN SMS İLE GELEN ONAY KODUNU SOYLEYİN"
  - gizlilik_baskisi: "ARAMİZDA KALSİN"

### tes-kargo_07-003
MESAJ: SON UYARI: gonderiniz  yarin  saat 19:00 itibariyla iade edilecek. Gumruk harci 118,49₺, odeme  sayfasi: https://cutt.ly/0HhPNwS
TÜR: sahte_kargo_gumruk
KANITLAR:
  - aciliyet: "yarin  saat 19:00 itibariyla iade edilecek"
  - odeme_talebi: "Gumruk harci 118,49₺"
  - link: "https://cutt.ly/0HhPNwS"

### tes-odul_07-002
MESAJ: POYRAZ KART MÜŞTERİLERİNE ÖZEL: HARCAMALARINIZIN 2.952,49 TL'Sİ İADE EDİLECEK. İADE İÇİN CVV VE SON KULLANMA TARİHİNİ GİRİN HTTP://POYRAZAKRT.CLİCK/1422
TÜR: odul_kampanya
KANITLAR:
  - odul_vaadi: "HARCAMALARINIZIN 2.952,49 TL'Sİ İADE EDİLECEK"
  - kimlik_talebi: "İADE İÇİN CVV VE SON KULLANMA TARİHİNİ GİRİN"
  - link: "HTTP://POYRAZAKRT.CLİCK/1422"

### tes-reklam_07-005
MESAJ: Poyraz Kart sahiplerine akaryakıtta %15 indirim fırsatı 11.08.2026 tarihine kadar. Detaylar https://poyrazkart.com.tr/kampanya adresinde. Ret için 7000'e RET yazın. Mersis: 0960043474953998
TÜR: reklam_spam
KANITLAR:
  (yok)

### tes-kurum_07-009
MESAJ: Pazaryolu hesabınızda olağandışı griş tespit edildi. Hessabınızı korumak için şifrenizi yenileyin pazaryolu-tr.xyz 2 saat içinde işlem yapılmazsa hesabınız silinir
TÜR: kurum_taklidi
KANITLAR:
  - kimlik_talebi: "Hessabınızı korumak için şifrenizi yenileyin"
  - link: "pazaryolu-tr.xyz"
  - aciliyet: "2 saat içinde işlem yapılmazsa hesabınız silinir"

### tes-mesru_06-009
MESAJ: Pazaryolu siparisiniz onaylandi. Siparis tutari 791,50 TL. Tahmini teslim 27.01.2026. Giris kodunuz [OTP], kimseyle paylasmayiniz.
TÜR: mesru_islem
KANITLAR:
  (yok)

### tes-reklam_07-011
MESAJ: Poyraz Kart sahiplerine akaryakıtta %25 indirim fırsatı 19.09.2026 tarihine kadar. Detaylar www.poyrazkart.com.tr/fatura adresinde. Ret için 7000'e RET yazın. Mersis: 0895814097876525
TÜR: reklam_spam
KANITLAR:
  (yok)

### tes-odul_07-008
MESAJ: Poyraz Kart müşterilerine özel: harcamalarınızın 1.852 TL'si iade edilecek. İade için CVV ve son kullanma tarihini girin https://poyrazkart-guvenlik.monster/tr/islem
TÜR: odul_kampanya
KANITLAR:
  - odul_vaadi: "harcamalarınızın 1.852 TL'si iade edilecek"
  - kimlik_talebi: "İade için CVV ve son kullanma tarihini girin"
  - link: "https://poyrazkart-guvenlik.monster/tr/islem"

### tes-kurum_06-010
MESAJ: Sedirbank: mobil şubeniz yeni cihazda açıldı. Siz değilseniz hemen bilgilerinizi güncelleyin https://esedirbank.top/odeme
TÜR: kurum_taklidi
KANITLAR:
  - kurum_taklidi: "Sedirbank: mobil şubeniz yeni cihazda açıldı"
  - aciliyet: "hemen"
  - kimlik_talebi: "bilgilerinizi güncelleyin"

### tes-kargo_06-011
MESAJ: Merhaba,  Turna  Kargo  subesinde adiniza  kayitli  bir koli var. Teslim almak icin kart  bilgilerinizi dogrulayin  www.turnakargo-destek.top Hizmet bedeli 19,50  TL
TÜR: sahte_kargo_gumruk
KANITLAR:
  - kimlik_talebi: "Teslim almak icin kart  bilgilerinizi dogrulayin"
  - link: "www.turnakargo-destek.top"
  - odeme_talebi: "Hizmet bedeli 19,50  TL"

### tes-oyun_06-012
MESAJ: Zirvearena: 306 lira degerinde cuzdan bakiyesi hediye! Hesabini bagla ve kodu onayla cutt.ly/fy1d9
TÜR: oyun_hesap_skin
KANITLAR:
  - odul_vaadi: "306 lira degerinde cuzdan bakiyesi hediye"
  - kimlik_talebi: "Hesabini bagla ve kodu onayla"
  - link: "cutt.ly/fy1d9"

### tes-oyun_06-010
MESAJ: Zirvearena: 2.245,49 lira değerinde cüzdan bakiyesi hediye! Hesabını bağla ve kodu onayla https://s.id/qYWR2s
TÜR: oyun_hesap_skin
KANITLAR:
  - odul_vaadi: "2.245,49 lira değerinde cüzdan bakiyesi hediye"
  - kimlik_talebi: "Hesabını bağla ve kodu onayla"
  - link: "https://s.id/qYWR2s"

### tes-yatirim_07-007
MESAJ: LİMAN PORTFÖY: PORTFÖYÜNÜZDE 36.829₺ KÂR BİRİKTİ. ÇEKİM İÇİN ÖNCE 4.658,49 TL KOMİSYON ÖDEMENİZ GEREKİYOR. BUGÜN ÖDEMEZSENİZ KÂRINIZ SIFIRLANIR.
TÜR: yatirim_vip_grup
KANITLAR:
  - odul_vaadi: "36.829₺ KÂR BİRİKTİ"
  - odeme_talebi: "ÇEKİM İÇİN ÖNCE 4.658,49 TL KOMİSYON ÖDEMENİZ GEREKİYOR"
  - aciliyet: "BUGÜN ÖDEMEZSENİZ KÂRINIZ SIFIRLANIR"

### tes-mesru_07-011
MESAJ: Kamu Portalı: 19.08.2026 günü saat 12:30 için hastane randevunuz oluşturulmuştur. İptal için randevu sistemini kullanınız.
TÜR: mesru_islem
KANITLAR:
  (yok)

### tes-gorev_06-008
MESAJ: Pazaryolu mağaza puanlama görevi: 3.457,50 TL komisyon. Siparişi önce kendi hesabınızdan 3.090 TL ile verin, iade ediyoruz. Görevli: [TEL]
TÜR: gorev_is_ilani
KANITLAR:
  - odul_vaadi: "3.457,50 TL komisyon"
  - odeme_talebi: "Siparişi önce kendi hesabınızdan 3.090 TL ile verin"
  - kanal_degistirme: "Görevli: [TEL]"

### tes-kurum_07-002
MESAJ: Pazaryolu hesabinizda olagandisi giris tespit edildi. Hesabinizi korumak icin sifrenizi yenileyin pazayrolu.live/giris 24 saat icinde islem yapilmazsa hesabiniz silinir
TÜR: kurum_taklidi
KANITLAR:
  - kimlik_talebi: "Hesabinizi korumak icin sifrenizi yenileyin"
  - link: "pazayrolu.live/giris"
  - aciliyet: "24 saat icinde islem yapilmazsa hesabiniz silinir"

### tes-kargo_06-008
MESAJ: Merhaba, Turna Kargo şubesinde adınıza kayıtlı bir koli var. Teslim almak için kart bilgilerinizi doğrulayın https://turnakargo-iade.info/5631 Hizmet bedeli 23,00₺
TÜR: sahte_kargo_gumruk
KANITLAR:
  - kimlik_talebi: "Teslim almak için kart bilgilerinizi doğrulayın"
  - link: "https://turnakargo-iade.info/5631"
  - odeme_talebi: "Hizmet bedeli 23,00₺"

### tes-mesru_06-011
MESAJ: Pazaryolu siparişiniz onaylandı. Sipariş tutarı 1.361₺. Tahmini teslim 25.03.2026. Giriş kodunuz [OTP], kimseyle paylaşmayınız.
TÜR: mesru_islem
KANITLAR:
  (yok)

### tes-reklam_06-006
MESAJ: Gökkuşağı Mobil fiber internette yeni yıl kampanyası: 12 ay boyunca 2.022 TL. Hemen başvurun: gokkusagimobil.com.tr/kampanya Ret için 3434
TÜR: reklam_spam
KANITLAR:
  (yok)

### tes-kurum_07-008
MESAJ: Pazaryolu hesabınızda olağandışı giriş tespit edildi. Hesabınızı korumak için şifrenizi yenileyin epazaryolu.cyou/tr/islem 24 saat içinde işlem yapılmazsa hesabınız silinir
TÜR: kurum_taklidi
KANITLAR:
  - kimlik_talebi: "Hesabınızı korumak için şifrenizi yenileyin"
  - link: "epazaryolu.cyou/tr/islem"
  - aciliyet: "24 saat içinde işlem yapılmazsa hesabınız silinir"

### tes-gorev_06-011
MESAJ: Pazzaryolu mağaza puanlama görevi: 2.196,99 TL komisoyn. Siparişi önce kendi hesabınızdan 1.416₺ ile verin, iade ediyoruz. Görevli: [TEL]
TÜR: gorev_is_ilani
KANITLAR:
  - odul_vaadi: "2.196,99 TL komisoyn"
  - odeme_talebi: "Siparişi önce kendi hesabınızdan 1.416₺ ile verin"
  - kanal_degistirme: "Görevli: [TEL]"

### tes-yakin_07-004
MESAJ: Teyze yeni numaramı kaydet, eskisi kapandı. Kiramı yatıramadım 4.922 lira gönderir misin aramızda kalsın
TÜR: yakin_taklidi
KANITLAR:
  - yakinlik_iddiasi: "Teyze yeni numaramı kaydet, eskisi kapandı"
  - odeme_talebi: "Kiramı yatıramadım 4.922 lira gönderir misin"
  - gizlilik_baskisi: "aramızda kalsın"

### tes-oyun_06-005
MESAJ: Zirvearena: 1.583₺ değerinde cüzdan bakiyesi hediye! Hesabını bağla ve kodu onayla https://rebrand.ly/vBgxiVK8
TÜR: oyun_hesap_skin
KANITLAR:
  - odul_vaadi: "1.583₺ değerinde cüzdan bakiyesi hediye"
  - kimlik_talebi: "Hesabını bağla ve kodu onayla"
  - link: "https://rebrand.ly/vBgxiVK8"

### tes-yatirim_07-000
MESAJ: Liman Portföy: Portföyünüzde 31.597 TL kâr birikti. Çekim için önce 2.924,49 TL komisyon ödemeniz gerekiyor. Bugün ödemezseniz kârınız sıfırlanır.
TÜR: yatirim_vip_grup
KANITLAR:
  - odul_vaadi: "31.597 TL kâr birikti"
  - odeme_talebi: "Çekim için önce 2.924,49 TL komisyon ödemeniz gerekiyor"
  - aciliyet: "Bugün ödemezseniz kârınız sıfırlanır"

### tes-yakin_07-002
MESAJ: 📦 Baba yeni numaraim kaydet, eskisi kapandi. Kirami yatirramadim 3.054 TL gonderir misin aramizda kalsin
TÜR: yakin_taklidi
KANITLAR:
  - yakinlik_iddiasi: "Baba yeni numaraim kaydet, eskisi kapandi"
  - odeme_talebi: "Kirami yatirramadim 3.054 TL gonderir misin"
  - gizlilik_baskisi: "aramizda kalsin"

### tes-odul_06-003
MESAJ: Şanslı müşterimiz seçildiniz, iPhone sizin! Sadece 48,99₺ sigorta bedeli ödeyin. Pazaroylu https://bit.ly/apUshiBd
TÜR: odul_kampanya
KANITLAR:
  - odul_vaadi: "Şanslı müşterimiz seçildiniz, iPhone sizin"
  - odeme_talebi: "Sadece 48,99₺ sigorta bedeli"
  - link: "https://bit.ly/apUshiBd"

### tes-mesru_06-010
MESAJ: Pazaryolu siparişiniz onaylandı. Sipariş tutarı 4.175₺. Tahmini teslim 18.10.2026. Giriş kodunuz [OTP], kimseyle paylaşmayınız.
TÜR: mesru_islem
KANITLAR:
  (yok)

### tes-odul_07-003
MESAJ: Poyraz Kart müşterilerine özel: harcamalarınızın 2.556 TL'si iade edilecek. İade için CVV ve son kullanma tarihini girin poyrazkart-destek.loan/dogrula
TÜR: odul_kampanya
KANITLAR:
  - odul_vaadi: "harcamalarınızın 2.556 TL'si iade edilecek"
  - kimlik_talebi: "İade için CVV ve son kullanma tarihini girin"
  - link: "poyrazkart-destek.loan/dogrula"

### tes-mesru_06-013
MESAJ: Pazaryolu siparisiniz onaylandi. Siparis tutari 3.971,00 lira. Tahmini teslim 07.06.2026. Giris kodunuz [OTP], kimseyle paylasmayiniz.
TÜR: mesru_islem
KANITLAR:
  (yok)

### tes-yatirim_06-008
MESAJ: YAPAY ZEKÂ DESTEKLİ ROBOT İLE GÜNLÜK 4.587₺ PASİF GELİR! BAŞLANGIÇ PAKETİ SADECE 575,00 TL KAYIT İÇİN CHAT.WHATSAPP.COM/HCALRRT1M7
TÜR: yatirim_vip_grup
KANITLAR:
  - odul_vaadi: "YAPAY ZEKÂ DESTEKLİ ROBOT İLE GÜNLÜK 4.587₺ PASİF GELİR"
  - odeme_talebi: "BAŞLANGIÇ PAKETİ SADECE 575,00 TL"
  - kanal_degistirme: "KAYIT İÇİN CHAT.WHATSAPP.COM/HCALRRT1M7"

### tes-yakin_07-006
MESAJ: 📦 Abla yeni numaramı kaydet, eskisi kapandı. Kiramı yatıramadım 1.953 TL gönderir misin aramızda kalsın
TÜR: yakin_taklidi
KANITLAR:
  - yakinlik_iddiasi: "Abla yeni numaramı kaydet, eskisi kapandı"
  - odeme_talebi: "Kiramı yatıramadım 1.953 TL gönderir misin"
  - gizlilik_baskisi: "aramızda kalsın"

### tes-reklam_07-009
MESAJ: Poyraz Kart sahiplerine akaryakıtta %10 indirim fırsatı 25.12.2026 tarihine kadar. Detaylar www.poyrazkart.com.tr adresinde. Ret için 7000'e RET yazın. Mersis: 0174685639263144
TÜR: reklam_spam
KANITLAR:
  (yok)

### tes-mesru_07-002
MESAJ: Kamu Portalı: 19.10.2026 günü saat 12:00 için hastane randevunuz oluşturulmuştur. İtal için randevu sistemini kullanınız.
TÜR: mesru_islem
KANITLAR:
  (yok)

### tes-mesru_07-009
MESAJ: Kamu Portalı: 07.06.2026 günü saat 09:00 için hastane randevunuz oluşturulmuştur. İptal için randevu sistemini kullanınız.
TÜR: mesru_islem
KANITLAR:
  (yok)

### tes-bahis_06-012
MESAJ: ⚠️ Sike garantili mac listesi geldi, oranlar cok yuksek. Listeyi almak icin 2.173 TL yatir [TEL] WhatsApp
TÜR: yasa_disi_bahis
KANITLAR:
  - odul_vaadi: "Sike garantili mac listesi"
  - odeme_talebi: "Listeyi almak icin 2.173 TL yatir"
  - kanal_degistirme: "[TEL] WhatsApp"

### tes-mesru_07-006
MESAJ: Kamu Portalı: 10.10.2026 günü saat 16:15 için hastane randevunuz oluşturulmuştur. İptal için randevu sistemini kullanınız.
TÜR: mesru_islem
KANITLAR:
  (yok)

### tes-bahis_06-007
MESAJ: Sike garantili mac listesi geldi, oranlar cok yuksek. Listeyi almak icin 284,50 TL yatir [TEL] WhatsApp
TÜR: yasa_disi_bahis
KANITLAR:
  - odul_vaadi: "Sike garantili mac listesi"
  - odeme_talebi: "Listeyi almak icin 284,50 TL yatir"
  - kanal_degistirme: "[TEL] WhatsApp"

### tes-yatirim_06-004
MESAJ: Yapay zekâ destekli robot ile günlük 1.117,90 TL pasif gelir! Başlangıç paketi sadece 351,49₺ Kayıt için t.me/+CWUfT7WhqD
TÜR: yatirim_vip_grup
KANITLAR:
  - odul_vaadi: "Yapay zekâ destekli robot ile günlük 1.117,90 TL pasif gelir"
  - odeme_talebi: "Başlangıç paketi sadece 351,49₺"
  - kanal_degistirme: "Kayıt için t.me/+CWUfT7WhqD"

### tes-yatirim_06-007
MESAJ: Yapay zekâ destekli  robot ile günlük  1.589 TL  pasif gelir! Başangıç paketi  sadece  2.601₺  Kayıt için t.me/+QOpUToMEFo
TÜR: yatirim_vip_grup
KANITLAR:
  - odul_vaadi: "Yapay zekâ destekli  robot ile günlük  1.589 TL  pasif gelir"
  - odeme_talebi: "Başangıç paketi  sadece  2.601₺"
  - kanal_degistirme: "Kayıt için t.me/+QOpUToMEFo"

### tes-yatirim_06-010
MESAJ: Yapay zekâ destekli robot ile günlük 3.951 TL pasif gelir! Başlangıç paketi sadece 2.771,00₺ Kayıt için https://t.me/limanportfoyvip
TÜR: yatirim_vip_grup
KANITLAR:
  - odul_vaadi: "Yapay zekâ destekli robot ile günlük 3.951 TL pasif gelir"
  - odeme_talebi: "Başlangıç paketi sadece 2.771,00₺"
  - kanal_degistirme: "Kayıt için https://t.me/limanportfoyvip"

### tes-yatirim_07-012
MESAJ: Liman Portföy: Portföyünüzde 40.849 TL kâr birikti. Çekim için önce 1.446,49 TL komisyon ödemeniz gerekiyor. Bugün ödemezseniz kârınız sıfırlanır.
TÜR: yatirim_vip_grup
KANITLAR:
  - odul_vaadi: "40.849 TL kâr birikti"
  - odeme_talebi: "Çekim için önce 1.446,49 TL komisyon ödemeniz gerekiyor"
  - aciliyet: "Bugün ödemezseniz kârınız sıfırlanır"

### tes-gorev_07-002
MESAJ: İş başvurunuz onaylandı! Haftalık 65.634 TL kazanç için kargo ve paketleme kiti 4.447,00 lira Detaylar için şu numaraya yazın [TEL]
TÜR: gorev_is_ilani
KANITLAR:
  - odul_vaadi: "Haftalık 65.634 TL kazanç"
  - odeme_talebi: "kargo ve paketleme kiti 4.447,00 lira"
  - kanal_degistirme: "Detaylar için şu numaraya yazın [TEL]"

### tes-bahis_07-011
MESAJ: Erişim engeli yok! sahabet yeni domain: sahabet410.top Üye ol 497,00 lira bedava bahis
TÜR: yasa_disi_bahis
KANITLAR:
  - link: "sahabet410.top"
  - odul_vaadi: "Üye ol 497,00 lira bedava bahis"

### tes-oyun_07-012
MESAJ: abi oyun içi parayı yarı fiyatına satıyorum 727,50 TL'ye 10.000 elmas, hesabına yüklemem için gelen kodu at moderatörlere söyleme banlarlar
TÜR: oyun_hesap_skin
KANITLAR:
  - odeme_talebi: "727,50 TL'ye 10.000 elmas"
  - kod_talebi: "hesabına yüklemem için gelen kodu at"
  - gizlilik_baskisi: "moderatörlere söyleme banlarlar"

### tes-oyun_07-002
MESAJ: abi oyun içi parayı yarı fiyatına satıyorum 2.145,99 TL'ye 10.000 elmas, hesabına yüklemem için gelen kodu at moderatörlere söyleme banlarlar
TÜR: oyun_hesap_skin
KANITLAR:
  - odeme_talebi: "2.145,99 TL'ye 10.000 elmas"
  - kod_talebi: "hesabına yüklemem için gelen kodu at"
  - gizlilik_baskisi: "moderatörlere söyleme banlarlar"

### tes-yakin_07-001
MESAJ: Annecim yeni numaramı kaydet, eskisi kapandı. Kiramı yatıramadım 3.351 TL gönderir misin aramızda kalsın
TÜR: yakin_taklidi
KANITLAR:
  - yakinlik_iddiasi: "Annecim yeni numaramı kaydet, eskisi kapandı"
  - odeme_talebi: "Kiramı yatıramadım 3.351 TL gönderir misin"
  - gizlilik_baskisi: "aramızda kalsın"

### tes-kurum_06-011
MESAJ: Ilgaz Bank: mobil subeniz yeni cihazda acildi. Siz degisleniz hemeen bilgilerinizi guncelleyin http://ilgazbank-tr.live/5537
TÜR: kurum_taklidi
KANITLAR:
  - kurum_taklidi: "Ilgaz Bank: mobil subeniz yeni cihazda acildi"
  - aciliyet: "hemeen"
  - kimlik_talebi: "bilgilerinizi guncelleyin"

### tes-kargo_06-013
MESAJ: Merhaba,  Turna Kargo şubesinde  adınıza kayıtlı bir  koli var.  Teslim almak  için kart bilgilerinizi doğrulayın www.turnakargo-iade.buzz/dogrula Hizmet bedeli 30,49 TL
TÜR: sahte_kargo_gumruk
KANITLAR:
  - kimlik_talebi: "Teslim almak  için kart bilgilerinizi doğrulayın"
  - link: "www.turnakargo-iade.buzz/dogrula"
  - odeme_talebi: "Hizmet bedeli 30,49 TL"

### tes-kurum_06-009
MESAJ: Ilgaz Bank: mobil şubeniz yeni cihazda açıldı. Siz değilseniz hemen bilgilerinizi güncelleyin www.ilgazbankgiris.win/1226
TÜR: kurum_taklidi
KANITLAR:
  - kurum_taklidi: "Ilgaz Bank: mobil şubeniz yeni cihazda açıldı"
  - aciliyet: "hemen"
  - kimlik_talebi: "bilgilerinizi güncelleyin"

### tes-mesru_06-006
MESAJ: Pazaryolu siparisiniz onaylandi. Siparis tutari 4.955 TL. Tahmini teslim 12.11.2026. Giris kodunuz [OTP], kimseyle paylasmayiniz.
TÜR: mesru_islem
KANITLAR:
  (yok)

### tes-odul_07-010
MESAJ: Poyraz Kart musterilerine ozel: harcamalarinizin 1.332,50 TL'si iade edilecek. Iade icin CVV ve son kullanma tarihini girin https://poyrazkartonline.icu/dogrula
TÜR: odul_kampanya
KANITLAR:
  - odul_vaadi: "harcamalarinizin 1.332,50 TL'si iade edilecek"
  - kimlik_talebi: "Iade icin CVV ve son kullanma tarihini girin"
  - link: "https://poyrazkartonline.icu/dogrula"

### tes-yatirim_07-002
MESAJ: Liman Portföy: Portföyünüzde 51.822₺ kâr birikti. Çekim için önce 1.167,99 lira komisyon ödemeniz gerekiyor. Bugün ödemezseniz kârınız sıfırlanır.
TÜR: yatirim_vip_grup
KANITLAR:
  - odul_vaadi: "51.822₺ kâr birikti"
  - odeme_talebi: "Çekim için önce 1.167,99 lira komisyon ödemeniz gerekiyor"
  - aciliyet: "Bugün ödemezseniz kârınız sıfırlanır"

### tes-kargo_06-007
MESAJ: Merhaba, Turna Kargo şubesinde adınıza kayıtlı bir koli var. Teslim almak için kart bilgilerinizi doğrulayın turnakargo-tr.win/tr/islem Hizmet bedeli 114,50 TL
TÜR: sahte_kargo_gumruk
KANITLAR:
  - kimlik_talebi: "Teslim almak için kart bilgilerinizi doğrulayın"
  - link: "turnakargo-tr.win/tr/islem"
  - odeme_talebi: "Hizmet bedeli 114,50 TL"

### tes-reklam_07-004
MESAJ: Poyraz Kart sahiplerine akaryakıtta %30 indirim fırsatı 27.12.2026 tarihine kadar. Detaylar poyrazkart.com.tr/takip adresinde. Ret için 3434'e RET yazın. Mersis: 0955292896665256
TÜR: reklam_spam
KANITLAR:
  (yok)

### tes-kamu_06-005
MESAJ: Il Emniyet Mudurlugu Mali  Sube: Ilgaz Bank kartiniz yasa  disi bahiste kullanilmis. Hesabinizin  dondurulmamasi icin SMS ile geleen onay kodunu  soyleyin, aramizda kalsin.
TÜR: sahte_kamu_gorevlisi
KANITLAR:
  - yetki_iddiasi: "Il Emniyet Mudurlugu Mali  Sube: Ilgaz Bank kartiniz yasa  disi bahiste"
  - kod_talebi: "Hesabinizin  dondurulmamasi icin SMS ile geleen onay kodunu  soyleyin"
  - gizlilik_baskisi: "aramizda kalsin"

### tes-reklam_07-007
MESAJ: Poyraz Kart sahiplerine akaryakitta %30 indirim firsati 12.08.2026 tarihine kadar. Detaylar poyrazkart.com.tr/takip adresinde. Ret icin 4848'e RET yazin. Mersis: 0680150413345592
TÜR: reklam_spam
KANITLAR:
  (yok)

### tes-mesru_07-001
MESAJ: 📦 Kamu Portali: 06.09.2026 gunu saat 15:45 icin hastane randevunuz olusturulmustur. Iptal icin randevu sistemini kullaniniz.
TÜR: mesru_islem
KANITLAR:
  (yok)

### tes-oyun_06-006
MESAJ: Zirvearena: 667 TL değerinde cüzdan bakiyesi heiye! Hesabını bağla ve kodu onayla t.co/hnLjar
TÜR: oyun_hesap_skin
KANITLAR:
  - odul_vaadi: "667 TL değerinde cüzdan bakiyesi heiye"
  - kimlik_talebi: "Hesabını bağla ve kodu onayla"
  - link: "t.co/hnLjar"

### tes-gorev_07-005
MESAJ: Is basvurunuz onaylandi! Haftalik 75.789 lira kazanc icin kargo ve paketleme kiti 1.300₺ Detaylar icin su numaraya yazin [TEL]
TÜR: gorev_is_ilani
KANITLAR:
  - odul_vaadi: "Haftalik 75.789 lira kazanc"
  - odeme_talebi: "kargo ve paketleme kiti 1.300₺"
  - kanal_degistirme: "Detaylar icin su numaraya yazin [TEL]"

### tes-yatirim_06-006
MESAJ: Yapay zekâ destekli robot ile günlük 4.933 TL pasif gelir! Başlangıç paketi sadece 2.831 TL Kayıt için t.me/+PP6isRGShi
TÜR: yatirim_vip_grup
KANITLAR:
  - odul_vaadi: "Yapay zekâ destekli robot ile günlük 4.933 TL pasif gelir"
  - odeme_talebi: "Başlangıç paketi sadece 2.831 TL"
  - kanal_degistirme: "Kayıt için t.me/+PP6isRGShi"

### tes-kargo_06-002
MESAJ: Merhaba, Turna Kargo şubesinde adınıza kayıtlı bir koli var. Teslim almak için kart bilgilerinizi doğrulayın https://turnakargo-iade.win Hizmet bedeli 111,49 TL
TÜR: sahte_kargo_gumruk
KANITLAR:
  - kimlik_talebi: "Teslim almak için kart bilgilerinizi doğrulayın"
  - link: "https://turnakargo-iade.win"
  - odeme_talebi: "Hizmet bedeli 111,49 TL"

### tes-oyun_06-000
MESAJ: Zirvearena: 2.696,49 TL değerinde cüzdan bakiyesi hediye!  Hesabını bağla ve  kodu  onayla tinyurl.com/dgfbK6uJ
TÜR: oyun_hesap_skin
KANITLAR:
  - odul_vaadi: "2.696,49 TL değerinde cüzdan bakiyesi hediye"
  - kimlik_talebi: "Hesabını bağla ve  kodu  onayla"
  - link: "tinyurl.com/dgfbK6uJ"

### tes-bahis_07-002
MESAJ: Adres güncellendi! sahabet yeni domain: https://sahabet173.top Üye ol 3.815 TL bedava bahis
TÜR: yasa_disi_bahis
KANITLAR:
  - link: "https://sahabet173.top"
  - odul_vaadi: "Üye ol 3.815 TL bedava bahis"

### tes-yakin_06-010
MESAJ: Anecim benim, yurt dışındayım kartım bloke oldu, otel için 4.725₺ lzaım arkadaşın hesabına at [IBAN] çok acil lütfen
TÜR: yakin_taklidi
KANITLAR:
  - yakinlik_iddiasi: "Anecim benim, yurt dışındayım kartım bloke oldu"
  - odeme_talebi: "otel için 4.725₺ lzaım arkadaşın hesabına at [IBAN]"
  - aciliyet: "çok acil lütfen"

### tes-yakin_06-005
MESAJ: Annecim benim, yurt dışındayım kartım bloke oldu, otel için 528,90 lira lazım arkadaşın hesabına at [IBAN] çok acil lütfen
TÜR: yakin_taklidi
KANITLAR:
  - yakinlik_iddiasi: "Annecim benim, yurt dışındayım kartım bloke oldu"
  - odeme_talebi: "otel için 528,90 lira lazım arkadaşın hesabına at [IBAN]"
  - aciliyet: "çok acil lütfen"

### tes-kargo_06-010
MESAJ: !!️ Merhaba, Turna Kargo  şubesinde  adınzıa kayıtlı  bir koli var. Teeslim almak için kart  bilgilerinizi doğrulayın turnakargo-iade.com/odeme Hizmet  beeli  131,50  lira
TÜR: sahte_kargo_gumruk
KANITLAR:
  - kimlik_talebi: "Teeslim almak için kart  bilgilerinizi doğrulayın"
  - link: "turnakargo-iade.com/odeme"
  - odeme_talebi: "Hizmet  beeli  131,50  lira"

### tes-bahis_06-004
MESAJ: Sike garantili mac listesi geldi, oranlar cok yuksek. Listeyi almak icin 3.928₺ yatir [TEL] WhatsApp
TÜR: yasa_disi_bahis
KANITLAR:
  - odul_vaadi: "Sike garantili mac listesi"
  - odeme_talebi: "Listeyi almak icin 3.928₺ yatir"
  - kanal_degistirme: "[TEL] WhatsApp"

### tes-kamu_06-003
MESAJ: Il Emniyet Mudurlugu Mali Sube: Sedirbank kartiniz yasa disi bahiste kullanilmis. Hesabinizin dondurulmamasi icin SMS ile gelen onay kodunu soyleyin, aramizda kalsin.
TÜR: sahte_kamu_gorevlisi
KANITLAR:
  - yetki_iddiasi: "Il Emniyet Mudurlugu Mali Sube: Sedirbank kartiniz yasa disi bahiste kullanilmis"
  - kod_talebi: "Hesabinizin dondurulmamasi icin SMS ile gelen onay kodunu soyleyin"
  - gizlilik_baskisi: "aramizda kalsin"

### tes-kamu_07-003
MESAJ: SAYIN VATANDAŞIMIZ, HAKKINIZDA DOLANDIRICILIK SORUŞTURMASI BAŞLATILMIŞTIR. DOSYA NUMARANIZ İÇİN [TEL] NUMARALI SAVCILIK HATTINI ARAYIN. 1 SAAT İÇİNDE ARAMAZSANIZ GIYABINIZDA İŞLEM YAPILACAKTIR.
TÜR: sahte_kamu_gorevlisi
KANITLAR:
  - yetki_iddiasi: "HAKKINIZDA DOLANDIRICILIK SORUŞTURMASI BAŞLATILMIŞTIR"
  - kanal_degistirme: "DOSYA NUMARANIZ İÇİN [TEL] NUMARALI SAVCILIK HATTINI ARAYIN"
  - aciliyet: "1 SAAT İÇİNDE ARAMAZSANIZ GIYABINIZDA İŞLEM YAPILACAKTIR"

### tes-odul_07-004
MESAJ: Poyraz Kart musterilerine ozel: harcamalarinizin 1.536 TL'si iade edilecek. Iade icin CVV ve son kullanma tarihini girin https://poyrazkartgiris.win/giris
TÜR: odul_kampanya
KANITLAR:
  - odul_vaadi: "harcamalarinizin 1.536 TL'si iade edilecek"
  - kimlik_talebi: "Iade icin CVV ve son kullanma tarihini girin"
  - link: "https://poyrazkartgiris.win/giris"

### tes-kamu_07-012
MESAJ: Sayın  vatandaşımız, hakkınızda dolandırıcılık soruşturması başlatılmıştır. Dosya numaranız için  [TEL] numaralı  savcılık hattını  arayın.  3 gün  içinde  aramazsanız gıyabınızda  işlem yapılacaktır.
TÜR: sahte_kamu_gorevlisi
KANITLAR:
  - yetki_iddiasi: "hakkınızda dolandırıcılık soruşturması başlatılmıştır"
  - kanal_degistirme: "Dosya numaranız için  [TEL] numaralı  savcılık hattını  arayın"
  - aciliyet: "3 gün  içinde  aramazsanız gıyabınızda  işlem yapılacaktır"

### tes-gorev_07-011
MESAJ: İş başvurunuz onaylandı! Haftalık 55.447 TL kazanç için kargo ve paketleme kiti 3.321 TL Detaylar için şu numaraya yazın [TEL]
TÜR: gorev_is_ilani
KANITLAR:
  - odul_vaadi: "Haftalık 55.447 TL kazanç"
  - odeme_talebi: "kargo ve paketleme kiti 3.321 TL"
  - kanal_degistirme: "Detaylar için şu numaraya yazın [TEL]"

### tes-yakin_07-010
MESAJ: Babacım yeni numaramı kaydet, eskisi kapandı. Kiramı yatıramadım 4.205₺ gönderir misin aramızda kalsın
TÜR: yakin_taklidi
KANITLAR:
  - yakinlik_iddiasi: "Babacım yeni numaramı kaydet, eskisi kapandı"
  - odeme_talebi: "Kiramı yatıramadım 4.205₺ gönderir misin"
  - gizlilik_baskisi: "aramızda kalsın"

### tes-yatirim_07-008
MESAJ: !!️ Liman Portföy: Portföyünüzde  47.983  TL kâr birikti. Çekim için  önce  667 TL  komisyon  ödemeniz gerekiyor. Bugün ödemezseniz kârınız sıfırlanır.
TÜR: yatirim_vip_grup
KANITLAR:
  - odul_vaadi: "47.983  TL kâr birikti"
  - odeme_talebi: "Çekim için  önce  667 TL  komisyon  ödemeniz gerekiyor"
  - aciliyet: "Bugün ödemezseniz kârınız sıfırlanır"

### tes-odul_06-005
MESAJ: Şanslı müşterimiz seçildiniz, iPhone sziin! Sadeece 104,90₺ sigorta bedeli ödeyin. Pazaryolu https://t.co/PVhHX
TÜR: odul_kampanya
KANITLAR:
  - odul_vaadi: "Şanslı müşterimiz seçildiniz, iPhone sziin"
  - odeme_talebi: "Sadeece 104,90₺ sigorta bedeli"
  - link: "https://t.co/PVhHX"

### tes-kargo_07-002
MESAJ: SON UYARI: gönderiniz yarın saat 09:30 itibarıyla iade edilecek. Gümrük harcı 127,50 TL, ödeme sayfası: rebrand.ly/WTsVeQ5j
TÜR: sahte_kargo_gumruk
KANITLAR:
  - aciliyet: "yarın saat 09:30 itibarıyla iade edilecek"
  - odeme_talebi: "Gümrük harcı 127,50 TL"
  - link: "rebrand.ly/WTsVeQ5j"

### tes-bahis_06-005
MESAJ: Sike garantili mac listesi geldi, oranlar cok yuksek. Listeyi almak icin 3.630,99₺ yatir [TEL] WhatsApp
TÜR: yasa_disi_bahis
KANITLAR:
  - odul_vaadi: "Sike garantili mac listesi"
  - odeme_talebi: "Listeyi almak icin 3.630,99₺ yatir"
  - kanal_degistirme: "[TEL] WhatsApp"

### tes-oyun_07-006
MESAJ: abi oyun içi parayı yarı fiyatına satıyorum 1.157,50 TL'ye 10.000 elmas, hesabına yüklemem için gelen kodu at moderatörlere söyleme banlarlar
TÜR: oyun_hesap_skin
KANITLAR:
  - odeme_talebi: "1.157,50 TL'ye 10.000 elmas"
  - kod_talebi: "hesabına yüklemem için gelen kodu at"
  - gizlilik_baskisi: "moderatörlere söyleme banlarlar"

### tes-kurum_07-005
MESAJ: Pazaryolu hesabınızda olağandışı giriş tespit edildi. Hesabınzıı korumak için şifrenizi yenileyin pazaryolu-tr.loan/giris 30 dakika içinde işlem yapılmazsa hesabınız silinir
TÜR: kurum_taklidi
KANITLAR:
  - kimlik_talebi: "Hesabınzıı korumak için şifrenizi yenileyin"
  - link: "pazaryolu-tr.loan/giris"
  - aciliyet: "30 dakika içinde işlem yapılmazsa hesabınız silinir"

### tes-kurum_06-005
MESAJ: Ilgaz Bank: mobil subeniz yeni cihazda acildi. Siz degilseniz hemen bilgilerinizi guncelleyin http://ilgazbank-tr.com/5618
TÜR: kurum_taklidi
KANITLAR:
  - kurum_taklidi: "Ilgaz Bank: mobil subeniz yeni cihazda acildi"
  - aciliyet: "hemen"
  - kimlik_talebi: "bilgilerinizi guncelleyin"

### tes-odul_07-012
MESAJ: Poyraz Kart müşterilerine özel: harcamalarınızın 2.844 TL'si iade edilecek. İade için CVV ve son kullanma tarihini girin poyrazkart-destek.win/dogrula
TÜR: odul_kampanya
KANITLAR:
  - odul_vaadi: "harcamalarınızın 2.844 TL'si iade edilecek"
  - kimlik_talebi: "İade için CVV ve son kullanma tarihini girin"
  - link: "poyrazkart-destek.win/dogrula"

### tes-kamu_06-010
MESAJ: İl Emniyet Müdürlüğü Mali Şube: Ilgaz Bank kartınız yasa dışı bahiste kulanılmış. Hesabınızın dondurulmaması için SMS ile gelen onay kodunu söyleyin, aramızda kalın.
TÜR: sahte_kamu_gorevlisi
KANITLAR:
  - yetki_iddiasi: "İl Emniyet Müdürlüğü Mali Şube: Ilgaz Bank kartınız yasa dışı bahiste kulanılmış"
  - kod_talebi: "Hesabınızın dondurulmaması için SMS ile gelen onay kodunu söyleyin"
  - gizlilik_baskisi: "aramızda kalın"

### tes-odul_07-000
MESAJ: Poyraz Kart musterilerine ozel: harcamalarinizin 2.444 TL'si iade edilecek. Iade icin CVV ve son kullanma tarihini girin https://poyrazkart-iade.live
TÜR: odul_kampanya
KANITLAR:
  - odul_vaadi: "harcamalarinizin 2.444 TL'si iade edilecek"
  - kimlik_talebi: "Iade icin CVV ve son kullanma tarihini girin"
  - link: "https://poyrazkart-iade.live"

### tes-odul_06-007
MESAJ: Şanslı müşterimiz seçildiniz, iPhone sizin! Sadece 102,49 TL sigorta bedeli ödeyin. Pazaryolu t.ly/Zl7Y2AKr
TÜR: odul_kampanya
KANITLAR:
  - odul_vaadi: "Şanslı müşterimiz seçildiniz, iPhone sizin"
  - odeme_talebi: "Sadece 102,49 TL sigorta bedeli"
  - link: "t.ly/Zl7Y2AKr"

### tes-bahis_06-003
MESAJ: Şike garantili maç listesi geldi, oranlar çok yüksek. Listeyi almak için 1.819 TL yatır [TEL] WhatsApp
TÜR: yasa_disi_bahis
KANITLAR:
  - odul_vaadi: "Şike garantili maç listesi"
  - odeme_talebi: "Listeyi almak için 1.819 TL yatır"
  - kanal_degistirme: "[TEL] WhatsApp"

### tes-kurum_06-012
MESAJ: Sedirbank: mobil şubeniz yeni cihazda açıldı. Siz değiseniz heemn bilgileriizi güncelleyin sedirbank-guvenlik.monster
TÜR: kurum_taklidi
KANITLAR:
  - kurum_taklidi: "Sedirbank: mobil şubeniz yeni cihazda açıldı"
  - aciliyet: "heemn"
  - kimlik_talebi: "bilgileriizi güncelleyin"

### tes-kargo_07-011
MESAJ: SON UYARI: gönderiniz yarın saat 18:00 itibarıyla iade edilecek. Gümrük harcı 66,50 lira, ödeme sayfası: t.ly/b8kqsQm
TÜR: sahte_kargo_gumruk
KANITLAR:
  - aciliyet: "yarın saat 18:00 itibarıyla iade edilecek"
  - odeme_talebi: "Gümrük harcı 66,50 lira"
  - link: "t.ly/b8kqsQm"

### tes-gorev_06-003
MESAJ: Pazaryolu magaza puanlama gorevi: 4.153 TL komisyon. Siparisi once kendi hesabinizdan 1.741 TL ile verin, iade ediyoruz. Gorevli: [TEL]
TÜR: gorev_is_ilani
KANITLAR:
  - odul_vaadi: "4.153 TL komisyon"
  - odeme_talebi: "Siparisi once kendi hesabinizdan 1.741 TL ile verin"
  - kanal_degistirme: "Gorevli: [TEL]"

### tes-kamu_06-000
MESAJ: İl Emniyet Müdürlüğü Mali Şube: Sedirbank kartınız yasa dışı bahiste kullanılmış. Hesabınızın dondurulmaması için SMS ile glen onay kodunu söyleyin, aramızda kalsın.
TÜR: sahte_kamu_gorevlisi
KANITLAR:
  - yetki_iddiasi: "İl Emniyet Müdürlüğü Mali Şube: Sedirbank kartınız yasa dışı bahiste kullanılmış"
  - kod_talebi: "Hesabınızın dondurulmaması için SMS ile glen onay kodunu söyleyin"
  - gizlilik_baskisi: "aramızda kalsın"

### tes-gorev_07-008
MESAJ: İş başvurunuz onaylandı! Haftalık 75.782 TL kazanç için kargo ve paketleme kiti 1.076 TL Detaylar için şu numaraya yazın [TEL]
TÜR: gorev_is_ilani
KANITLAR:
  - odul_vaadi: "Haftalık 75.782 TL kazanç"
  - odeme_talebi: "kargo ve paketleme kiti 1.076 TL"
  - kanal_degistirme: "Detaylar için şu numaraya yazın [TEL]"

### tes-kamu_06-007
MESAJ: İl Emniyet  Müdürlüğü Mali  Şube: Ilgaz Bank kartınız  yasa  dışı bahiste kullanılmış. Hesabınızın dondurulmaması için SMS ile gelen onay kodunu  söyleyin, aramızda kalsın.
TÜR: sahte_kamu_gorevlisi
KANITLAR:
  - yetki_iddiasi: "İl Emniyet  Müdürlüğü Mali  Şube: Ilgaz Bank kartınız  yasa  dışı bahiste"
  - kod_talebi: "Hesabınızın dondurulmaması için SMS ile gelen onay kodunu  söyleyin"
  - gizlilik_baskisi: "aramızda kalsın"

### tes-kurum_07-010
MESAJ: Pazaryolu hesabinizda olagandisi giris tespit edildi. Hesabinizi korumak icin sifrenizi yenileyin https://pazaryolugiris.icu 3 gun icinde islem yapilmazsa hesabiniz silinir
TÜR: kurum_taklidi
KANITLAR:
  - kimlik_talebi: "Hesabinizi korumak icin sifrenizi yenileyin"
  - link: "https://pazaryolugiris.icu"
  - aciliyet: "3 gun icinde islem yapilmazsa hesabiniz silinir"

### tes-yakin_06-002
MESAJ: Babacım benim, yurt dışındayım kartım bloke oldu, otel için 4.603 TL lazım arkadaşın hesabına at [IBAN] çok acil lütfen
TÜR: yakin_taklidi
KANITLAR:
  - yakinlik_iddiasi: "Babacım benim, yurt dışındayım kartım bloke oldu"
  - odeme_talebi: "otel için 4.603 TL lazım arkadaşın hesabına at [IBAN]"
  - aciliyet: "çok acil lütfen"

### tes-yatirim_06-012
MESAJ: Yapay zeka destekli robot ile gunluk 1.534 TL pasif gelir! Baslangic paketi sadece 2.349 TL Kayit icin https://t.me/limanportfoyvip
TÜR: yatirim_vip_grup
KANITLAR:
  - odul_vaadi: "Yapay zeka destekli robot ile gunluk 1.534 TL pasif gelir"
  - odeme_talebi: "Baslangic paketi sadece 2.349 TL"
  - kanal_degistirme: "Kayit icin https://t.me/limanportfoyvip"

### tes-gorev_07-000
MESAJ: İş  başvurunuz  onaylandı!  Haftalık 85.149 TL kazanç  için  kargo ve  paketleme kiti 4.535 lira Detaylar  için  şu numaraya  yazın  [TEL]
TÜR: gorev_is_ilani
KANITLAR:
  - odul_vaadi: "Haftalık 85.149 TL kazanç"
  - odeme_talebi: "kargo ve  paketleme kiti 4.535 lira"
  - kanal_degistirme: "Detaylar  için  şu numaraya  yazın  [TEL]"

### tes-kamu_06-017
MESAJ: İl Emniyet Müdürlüğü Mali Şube: Ilgaz Bank kartınız yasa dışı bahiste kullanılmış. Hesabınızın dondurulmaması için SMS ile gelen onay kodunu söyleyin, aramızda kalsın.
TÜR: sahte_kamu_gorevlisi
KANITLAR:
  - yetki_iddiasi: "İl Emniyet Müdürlüğü Mali Şube: Ilgaz Bank kartınız yasa dışı bahiste"
  - kod_talebi: "Hesabınızın dondurulmaması için SMS ile gelen onay kodunu söyleyin"
  - gizlilik_baskisi: "aramızda kalsın"

### tes-kamu_07-010
MESAJ: Sayın vatadnaşımız, hakkınızda dolandırıcılık soruşturmsı başlatılmıştır. Dosya numaranız için [TEL] numaralı savıclık hattını arayın. 30 dakika içinde aramazsanız gıyabınızda işlem yapılacaktır.
TÜR: sahte_kamu_gorevlisi
KANITLAR:
  - yetki_iddiasi: "hakkınızda dolandırıcılık soruşturmsı başlatılmıştır"
  - kanal_degistirme: "Dosya numaranız için [TEL] numaralı savıclık hattını arayın"
  - aciliyet: "30 dakika içinde aramazsanız gıyabınızda işlem yapılacaktır"

### tes-reklam_06-010
MESAJ: Gökkuşağı Mobil fiber internette yeni yıl kampanyası: 12 ay boyunca 3.452₺. Hemen başvurun: www.gokkusagimobil.com.tr/takip Ret için 7000
TÜR: reklam_spam
KANITLAR:
  (yok)

### tes-odul_07-009
MESAJ: Poyraz Kart müşterilerine özel: harcamalarınızın 3.606 TL'si iade edilecek. İade için CVV ve son kullanma tarihini girin poyrazkartgiris.cfd
TÜR: odul_kampanya
KANITLAR:
  - odul_vaadi: "harcamalarınızın 3.606 TL'si iade edilecek"
  - kimlik_talebi: "İade için CVV ve son kullanma tarihini girin"
  - link: "poyrazkartgiris.cfd"

### tes-gorev_07-003
MESAJ: İş başvurunuz onaylandı! Haftalık 88.987 lira kazanç için kargo ve paketleme kiti 4.823 TL Detaylar için şu numaraya yazın [TEL]
TÜR: gorev_is_ilani
KANITLAR:
  - odul_vaadi: "Haftalık 88.987 lira kazanç"
  - odeme_talebi: "kargo ve paketleme kiti 4.823 TL"
  - kanal_degistirme: "Detaylar için şu numaraya yazın [TEL]"

### tes-bahis_07-008
MESAJ: ⚠️ ADRES GÜNCELLENDİ! TRİBUNBET YENİ DOMAİN: HTTPS://TRİBUNBET699.COM ÜYE OL 1.291₺ BEDAVA BAHİS
TÜR: yasa_disi_bahis
KANITLAR:
  - link: "HTTPS://TRİBUNBET699.COM"
  - odul_vaadi: "ÜYE OL 1.291₺ BEDAVA BAHİS"

### tes-yakin_06-003
MESAJ: Baba benim,  yurt dışındayım  kartım bloke  oldu, otel için 1.497 lira lazım arkadaşın hesabına at  [IBAN] çok acil lütfen
TÜR: yakin_taklidi
KANITLAR:
  - yakinlik_iddiasi: "Baba benim,  yurt dışındayım  kartım bloke  oldu"
  - odeme_talebi: "otel için 1.497 lira lazım arkadaşın hesabına at  [IBAN]"
  - aciliyet: "çok acil lütfen"

### tes-odul_07-011
MESAJ: Poyraz Kart musterilerine ozel: harcamalarinizin 424 TL'si iade edilecek. Iade icin CVV ve son kullanma tarihini girin https://poyrazkartonline.info/dogrula
TÜR: odul_kampanya
KANITLAR:
  - odul_vaadi: "harcamalarinizin 424 TL'si iade edilecek"
  - kimlik_talebi: "Iade icin CVV ve son kullanma tarihini girin"
  - link: "https://poyrazkartonline.info/dogrula"

### tes-gorev_07-006
MESAJ: İş başvurunuz onaylandı! Haftalık 68.931 TL kazanç için kargo ve paketleme kiti 1.977 lira Detaylar için şu numaraya yazın [TEL]
TÜR: gorev_is_ilani
KANITLAR:
  - odul_vaadi: "Haftalık 68.931 TL kazanç"
  - odeme_talebi: "kargo ve paketleme kiti 1.977 lira"
  - kanal_degistirme: "Detaylar için şu numaraya yazın [TEL]"

### tes-odul_06-010
MESAJ: !!️ ŞANSLI MÜŞTERİMİZ SEÇİLDİNİZ, İPHONE SİZİN! SADECE 113,99₺ SİGORTA BEDELİ ÖDEYİN. PAZARYOLU HTTPS://T.LY/2UHQJAU
TÜR: odul_kampanya
KANITLAR:
  - odul_vaadi: "ŞANSLI MÜŞTERİMİZ SEÇİLDİNİZ, İPHONE SİZİN"
  - odeme_talebi: "SADECE 113,99₺ SİGORTA BEDELİ"
  - link: "HTTPS://T.LY/2UHQJAU"

### tes-kargo_07-004
MESAJ: SON UYARI: gönderiniz bugün saat 08:45 itibarıyla iade edilecek. Gümrük harcı 106,50 lira, ödeme sayfası: https://cutt.ly/jnfYes2
TÜR: sahte_kargo_gumruk
KANITLAR:
  - aciliyet: "bugün saat 08:45 itibarıyla iade edilecek"
  - odeme_talebi: "Gümrük harcı 106,50 lira"
  - link: "https://cutt.ly/jnfYes2"

### tes-mesru_06-007
MESAJ: Pazaryolu siparişiniz onaylandı. Sipariş tutarı 777,50₺. Tahmini teslim 01.07.2026. Giriş kodunuz [OTP], kimseyle paylaşmayınız.
TÜR: mesru_islem
KANITLAR:
  (yok)

### tes-kargo_06-005
MESAJ: 🔔 Merhaba, Turna Kargo şubesinde adınıza kayıtlı bir koli var. Teslim almak için kart bilgilerinizi doğrulayın turnakargo-destek.live Hizmet bedeli 131,90 TL
TÜR: sahte_kargo_gumruk
KANITLAR:
  - kimlik_talebi: "Teslim almak için kart bilgilerinizi doğrulayın"
  - link: "turnakargo-destek.live"
  - odeme_talebi: "Hizmet bedeli 131,90 TL"

### tes-kamu_07-004
MESAJ: Sayın vatandaşımız, hakkınızda dolandırıcılık soruşturması başlatılmıştır. Dosya numaranız için [TEL] numaralı savcılık hattını arayın. 24 saat içinde aramazsanız gıyabınızda işlem yapılacaktır.
TÜR: sahte_kamu_gorevlisi
KANITLAR:
  - yetki_iddiasi: "hakkınızda dolandırıcılık soruşturması başlatılmıştır"
  - kanal_degistirme: "Dosya numaranız için [TEL] numaralı savcılık hattını arayın"
  - aciliyet: "24 saat içinde aramazsanız gıyabınızda işlem yapılacaktır"

### tes-kargo_07-008
MESAJ: SON UYARI: gönderiniz bugün saat 09:00 itibarıyla iade edilecek. Gümrük harcı 139,90₺, ödeme sayfası: s.id/qKp2XyI
TÜR: sahte_kargo_gumruk
KANITLAR:
  - aciliyet: "bugün saat 09:00 itibarıyla iade edilecek"
  - odeme_talebi: "Gümrük harcı 139,90₺"
  - link: "s.id/qKp2XyI"
