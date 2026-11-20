# ADR-0004: Sistem asla "güvenli" demez

- **Durum:** Kabul edildi · 2026-11-19

## Bağlam
Bir sınıflandırıcının "dolandırıcılık bulamadım" sonucu, "bu mesaj güvenli" demek değildir. Yeni bir dolandırıcılık
kalıbı, modelin hiç görmediği bir şablon ya da kanıt kapısının her şeyi düşürmesi aynı "düşük risk" çıktısını üretebilir.
"Güvenli" etiketi kullanıcıyı (özellikle 60+) linke tıklamaya yöneltebilir. Yanlış negatifin bedeli yanlış pozitiften çok daha yüksek.

## Karar
- Kullanıcıya giden metinde (`SistemCevabi.mesaj`) "güvenli*, güvende, zararsız, sorun yok, endişe etmeyin, tehlikesiz"
  ailesi şema doğrulamasında **reddedilir** (Türkçe küçük harf + ASCII katlama sonrası düzenli ifade).
- En iyi durum ifadesi: "Belirgin bir dolandırıcılık işareti bulunamadı." + bağımsız doğrulama önerisi.
- Şema bozuk, zaman aşımı veya kapı sonrası boş kanıt + şüpheli deterministik sinyal → `risk=belirsiz` (fail-closed).

## Bedeli
- "güvenlik" kelimesi de yakalanır. Kendi metinlerimizde bu kelimeyi kullanmıyoruz ("bankanızın resmi numarası" gibi).
