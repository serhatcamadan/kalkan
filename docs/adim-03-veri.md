# Adım 3 — Sentetik veri, şablon bölmesi, adversarial set · v1 · 2026-11-20

## Tahminler (üretimden önce)
| # | Tahmin | Sonuç |
|---|---|---|
| D1 | Kanıt doğrulamasında (maskeli alıntı maskeli metinde) ≤ %3 örnek düşer | ✅ 0 düşüş (işaret yöntemi sayesinde). Yalnızca tekrar eleme: 164 |
| D2 | Dolandırıcılık örneklerinin ≥ %80'inde en az bir güçlü deterministik sinyal olur | ✅ %93.4 |
| D3 | Dolandırıcılık DIŞI örneklerin de ≥ %50'sinde güçlü sinyal olur → sinyaller tek başına ayırt edemez | ✅ %86.5 (tutar, link, OTP meşru mesajda da var) |
| D4 | Test→eğitim 8-gram örtüşmesi ≤ %30 | ✅ ama %0.0. Beklenenden temiz, sınırlama olarak not edildi |
| D5 | ASCII gürültü oranı ≈ %25 | ✅ %25–26 |

D3, yol haritasındaki **H3**'ün (TF-IDF tür bulur ama kanıt veremez) kardeşi: kural tabanlı sinyaller kanıt bulur
ama türe karar veremez. LLM'in yeri bu ikisinin arasında.

## Geliştirirken yakalanan hatalar (her biri için regresyon testi var)
1. **Çift boşluklu telefon/IBAN maskelenmiyordu** (`0599  885 86 14`). Veri testi (`test_model_girdisinde_ham_pii_yok`)
   yakaladı. Gerçek kullanıcı mesajında da olur. `pii.py` v1.1.
2. **Adında "rn" geçen marka** (Sar**n**ıçbank) görsel iskelette "m"ye dönüştüğü için marka içeren sahte alan adı kaçıyordu.
3. **Alt alan hilesi** `sarnicbank.com.tr.giris-dogrula.top` yakalanmıyordu.
4. **Yön değiştirme karakteri (RLO)** ile ters yazılmış link, kanonik metinde silinip iz bırakmıyordu → `gizli_karakter` sinyali.
5. Yazım gürültüsü kısa link alanını bozuyordu (`rebrrand.ly`) → gürültü artık yalnızca düz kelimelere uygulanıyor.

2–4'ü adversarial set buldu: set daha model eğitilmeden kendi kodumuzu test etmeye yaradı.

## Sayılar
`python tools/veri_istatistik.py` çıktısı: eğitim 1.496 · doğrulama 198 · test 297 · adversarial 30.
Ortalama hedef JSON 207 karakter (Adım 2 ölçümüyle ≈ 68 token → VPS 0.8B'de ≈ 3 sn üretim).
