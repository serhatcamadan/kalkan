# Kalkan: deney raporu · 2026-11-23

Bu rapor projenin **nasıl** bu sonuca vardığını anlatır: hangi hipotezler kuruldu, hangileri yanlış çıktı, neyi
neden değiştirdik. Her adımda tahminler ölçümden **önce** yazıldı ve sonuçla birlikte karne olarak tutuldu
(adım belgelerinde). Sayıların tamamı [eval raporunda](eval-report.md).

## 1. Soru ve karar kuralı

Bir bankanın ya da operatörün kendi sunucusunda, mesajı dışarı göndermeden çalışabilecek küçük bir model, Türkçe
dolandırıcılık mesajlarını **güvenilir biçimde** işaretleyebilir mi?

Karar kuralı ölçmeye başlamadan önce yazıldı (Adım 5). Golden sette dolandırıcılık recall ≥ 0.95, meşru FPR ≤ 0.05,
kapıdan önce kanıt geçerliliği ≥ 0.95 olmalı; adversarial sette sızıntı olmamalı; VPS'te p95 ≤ 15 sn olmalı.
Bunları geçenlerin en ucuzu seçilecekti. Sert kısıt: "banka modu" yerel olmak zorunda.

## 2. Taban çizgileri (Adım 4–6)

| | golden makro-F1 | gözlem |
|---|---|---|
| Kural | 0.887 | Güçlü, ama şablon diline yazıldı; gerçek e-postada (OLTA) recall 0.20 |
| TF-IDF | 0.491 | Şablonları ezberliyor |
| Qwen3.5-0.8B zero-shot | 0.128 | Her şeye alarm (FPR 1.0), JSON'u kesiyor |
| Qwen3.5-2B zero-shot | 0.236 | Kanıt yazmıyor (ort. 21 çıktı token'ı) |
| gpt-5.4-mini | 0.905 | Üst çizgi; ama bulut |

Zero-shot küçük modeller işe yaramadı. İnce ayar gerekiyordu.

## 3. İnce ayar: dört deneme, üç ders (Adım 7–8)

**v1 (tür başına 4 eğitim şablonu, 2 epoch).** Biçim mükemmel öğrenildi (JSON 1.000, birebir alıntı 0.99). Tür
doğruluğu ise **0.58** kaldı. Doğrulamadaki her karışıklık sayısı **18**'di. Bu, bir türün **bütün** örneklerinin
toplu halde yanlış türe gittiği anlamına geliyordu. Model türü anlamdan değil, 4 kalıba yüzey benzerliğinden
öğrenmişti. 300. iterasyondan sonra doğrulama kaybı yükseldi, yani ezber başladı.
→ **Ders 1:** 1.496 örnek aslında 44 kalıbın varyasyonuydu. Doğrulama da fiilen 11 "hep ya da hiç" ölçümüydü.

**v2 (tür başına 10 eğitim şablonu, ~1 epoch).** Kayıp düştü, ezber yumuşadı, ama tür doğruluğu **0.64**'te kaldı.
GGUF'a çevirip golden'da tam sistemle ölçtük: recall 1.000, ama **meşru mesajların %30'una alarm** verdi. Kuralı
birinci, modeli ikinci görüş yapan "katmanlı" bir karar bile FPR'yi yalnızca 0.26'ya indirdi. Model meşru onay
kodlarını "kod talebi" diye alıntılıyordu. Alıntı mesajda gerçekten geçtiği için kapı onu durduramıyordu.
→ **Ders 2:** eğitim verisinin yalnızca **%18**'i meşruydu (11 türün 9'u dolandırıcılık, her tür eşit). Model
"emin değilsem dolandırıcılık" önselini öğrenmişti.

**v3 (aynı ayarlar, tek değişken: %40 meşru).** Doğrulamada yanlış alarm %50'den **%0**'a indi. Golden'da tam sistemle
FPR **0.019** oldu. Katmanlı kararla birlikte makro-F1 **0.905**, recall **1.000** ve sızıntı 0 çıktı. Bu, gpt-5.4-mini
düzeyi; üstelik tamamen yerel. Durma kriteri (FPR ≤ 0.05, recall ≥ 0.95) deneyden önce yazılmıştı ve geçildi.

**Nicemleme.** Q4_K_M, MLX modeline göre tür doğruluğunu **−0.091** düşürdü ve bir dolandırıcılık şablonunu meşruya
kaydırdı. Q8_0 ise 0.985 uyumlu kaldı.
→ **Ders 3:** "Q4_K_M yeter" varsayımı küçük ve dar marjlı ince ayarlı bir modelde tutmuyor. Q8_0 VPS'te yine de
hedefin yarısının altında (p95 7,4 sn).

**Yan bulgu:** v1/v2 için yazdığım ek şablonlardan en çok TF-IDF yararlandı: golden 0.491'den 0.689'a çıktı, FPR 0
kaldı. Aynı veride doğrusal bir model, v2'yi geçti.

## 4. Katmanlı karar ve "ölçülen = çalışan" (Adım 8–9)

Katman kuralı golden'a **bakılmadan** seçildi: altı varyant ölçüldü, karar önceden yazılmış ★ varyantla verildi.
Böylece golden bir ayar setine dönüşmedi. Sonra aynı karar kodu hem servise hem değerlendirmeye taşındı. Bir
**tekrar oynatma testi**, kaydedilmiş model çıktılarını servise geri veriyor ve servisin her örnekte değerlendirmeyle
aynı riski ürettiğini doğruluyor. Gerçek sunucuyla yapılan uçtan uca ölçüm, çevrimdışı sonuçla birebir aynı çıktı.

Katmanın değeri canlıda görüldü. "Kestane Kargo … 49,90 TL ödeyin …" mesajını model **meşru** saydı. Kural yüksek
dedi, model riski düşüremediği için kullanıcı yüksek gördü. Model tek başına çalışsaydı bu mesaj "düşük" alırdı.

## 5. Güvenlik: üç açık bulundu, ikisi testle (Adım 9–11)

- **Kırpma saldırısı.** Ürün mesajın yalnızca ilk 2.000 karakterine bakıyordu. Dolandırıcılık, uzun ve zararsız bir
  metnin arkasına saklanabiliyordu. Bunun izi ölçümde de vardı: kural katmanı gerçek e-postalarda düştü. Düzeltme:
  kural ve sinyaller metnin tamamına bakıyor; kırpılan mesaj "düşük" alamıyor.
- **BYOK anahtarı.** Anahtar `repr` çıktısında gizliydi, ama yazdığım test `vars()` dökümünde onu **düz metin**
  buldu. Artık `_Gizli` sarmalayıcıda tutuluyor.
- **X-Forwarded-For.** API istemci IP'sini bu başlığın ilk öğesinden okuyordu. Caddy arkasında ilk öğeyi istemci
  kendisi yazabilir, yani hız sınırı aşılabilirdi. Düzeltme: son öğe okunuyor ve Caddy başlığı kendisi yazıyor. Testli.

**Kör saldırı seti.** 24 mesaj yazıldı ve sonuçlara bakmadan **bir kez** ölçüldü. Sistem ilk ölçümde 16 saldırıdan
2'sini kaçırdı. İkisinde de model doğru bulmuştu, ama "talep" kanıtı alıntılamadığı için katman yükseltmedi. Birinde
deterministik bir IBAN sinyali de vardı. Sentetik verilerde IBAN içeren **hiç** meşru mesaj yoktu, yani bu boşluk
hiçbir ölçümde görünemezdi. Politika v1.2 eklendi: "meşru" dense bile IBAN varsa sonuç "orta". Kuralın bedeli de
bilinçli olarak yazıldı: arkadaş arası "IBAN'ım şu" mesajı alarm alır. Tetikleyen örnek kör statüsünü kaybetti ve
yerine üç yeni kör örnek yazıldı; üçü de yakalandı. Son durum: **19 saldırıdan 1'i** sızıyor (BÜYÜK HARF + ASCII,
linksiz). Bu örnek bilerek düzeltilmedi: kör bir örneğe bakarak kural ayarlamak, kör seti ayar setine çevirirdi.

## 6. Kendi hatalarımız

Bir portföy projesinde bunlar saklanmamalı:

- **Dış set alıntıları repoya girdi.** Sonuç dosyalarına "mesaj metni yazılmaz" kuralı konmuştu, ama modelin kanıt
  alıntılarının da metin olduğu gözden kaçtı. Gerçek e-postalardan parçalar GitHub'a gitti. Bunlar zaten herkese
  açık veri setleriydi ve kişisel veriler maskeliydi. Yine de proje kuralı ihlal edildi. Dosyalar takipten ve git
  geçmişinden silindi, `.gitignore`'a eklendi, testle korundu. [Olay notu](olay-2026-11-22-dis-set-alintilari.md)
- **`yeniden_puanla` katmanlı sonuçları bozdu.** Politika değişince sonuçları modeli çağırmadan yeniden puanlayan araç,
  katmanlı sonuçları da katman mantığı olmadan yeniden puanladı. Fark edildi, eski değerler geri alındı, araç
  düzeltildi ve servisle eşitliği testlendi.
- **Doğrulanmamış varsayımlar:** var sanılan bir Docker imaj etiketi aslında yoktu. Bunun yerine aynı commit
  kaynaktan derlendi; ölçümler geçerli kaldı. Ayrıca bir `.gitignore` satırı fazla genişti (`logs/` →
  `training/logs` de kapsanıyordu), ve sertleştirme betiği hatayı gizleyip sessizce duruyordu.

## 7. Tahmin karnesi

Her adımda 4–6 tahmin ölçümden önce yazıldı. Yanlış çıkanlardan en öğreticileri:

- "Şablon çeşitliliği tür doğruluğunu 0.80'e taşır" (F7) → 0.64. Asıl sorun dengeydi.
- "v3 durma kriterini kıl payı geçemez" (D3) → FPR 0.019 ile rahatça geçti.
- "bf16 yuvarlama LoRA farkının %10–40'ını bozar" (G1) → %2.
- "Katmanlı yapı OLTA'da ayırt etmeyi +0.15 artırır" (K2) → v2 ile −0.03.

## 8. Sonuç

Mesajı dışarı göndermeden çalışan ve gpt-5.4-mini ile aynı golden skoruna ulaşan bir sistem kuruldu. Sistem
yerel, ücretsiz, ve 4 vCPU'luk bir VPS'te p95 6,9 sn'de cevap veriyor. Bunu tek başına model değil, **kural +
küçük model + kod tarafından doğrulanan kanıt** üçlüsü sağlıyor.

Ancak sonuç sentetik veride. Gerçek, izinli SMS ile bağımsız bir değerlendirme yapılmadan "üretime hazır" denemez.
Bir sonraki adım bu olurdu: gerçek meşru mesajlarla FPR'nin güven aralığını daraltmak ve kör seti büyütmek.
