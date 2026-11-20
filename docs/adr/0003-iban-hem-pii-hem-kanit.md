# ADR-0003: IBAN hem kişisel veri hem kanıt; sıra "önce sinyal, sonra maske"

- **Durum:** Kabul edildi · 2026-11-19

## Bağlam
"Şu IBAN'a 7.500 TL at" mesajında IBAN, dolandırıcılığın en güçlü kanıtlarından biri. Aynı zamanda bir kişinin
hesap numarası: modele, loglara ve BYOK sağlayıcısına ham haliyle gitmemeli. Aynı gerilim telefon numarası ve
kullanıcının yapıştırdığı canlı doğrulama kodu (OTP) için de geçerli.

## Karar
1. Deterministik sinyaller **kanonik metin** üzerinde, maskelemeden **önce** çıkarılır (`signals.cikar`).
   Ham değere bakarak hesaplanan bilgi (IBAN mod-97 geçerliliği gibi) sinyalin `ek` alanına yazılır;
   `deger` alanına ham PII asla yazılmaz (`[IBAN]`, `[TEL]`, `******`).
2. Ardından `pii.maskele(kanonik, ek_araliklar=OTP)` çalışır. Model, log ve denetim kaydı yalnızca maskeli metni görür.
3. Modelin kanıt alıntısı maskeli metne göre doğrulanır (kapı, Adım 5). Arayüz vurgusu `Maskeli.kanonige()` ile
   kanonik metne geri çevrilir. Kullanıcı kendi mesajını kendi tarayıcısında görür.

## Sonuçlar
- Model "TR00 …" görmez, "[IBAN]" görür. "IBAN'a para gönder" kalıbını öğrenmesi için yeterli; numaranın kendisi gereksiz.
- Sıra kuralı testle korunur (`test_iban_sinyali_maskeden_once_gecerlilikle`, `test_canli_otp_maskelenir_ve_sinyale_sizmaz`).
