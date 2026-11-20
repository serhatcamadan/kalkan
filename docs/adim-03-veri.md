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

## Golden inceleme · 1. tur: Gemini ön-elemesi (2026-11-20)
Yöntem: `tools/llm_inceleme.py` ile 150 örnek + yönerge Gemini'ye verildi. Sonuç: 137 doğru, 13 işaret.
13 işaretin tamamı **3 şablona** dayanıyordu:

| Şablon | Gemini'nin dediği | Değerlendirme | Ne yapıldı |
|---|---|---|---|
| yakin_06 (×8) | `yakinlik_iddiasi` kanıtı hitabı ("Babacım", "Dayı") içermiyor | ✅ Haklı: "yurt dışındayım" bir bahane, yakınlık iddiası hitapta | Hitap kanıtın içine alındı. Aynı kusur eğitim şablonlarında (yakin_01–05) da vardı, düzeltildi |
| reklam_07 (×2) | Ret mekanizması yok → tür `mesru_islem`/`sahte_kargo_gumruk` olmalı | ⚠️ **Belirti doğru, teşhis yanlış.** Şablon kendi taksonomimizle çelişiyordu (reklamda İYS ret satırı zorunlu), ama tür reklamdı | Şablona ret satırı eklendi, tür korundu |
| mesru_07 (×2) | 21:15 / 21:45'te hastane randevusu gerçekçi değil | ✅ Haklı | `SAAT_MESAI` slotu (08–16) |

Ders: LLM denetçi **hata yerini** iyi buluyor ama **önerdiği düzeltme** her zaman doğru değil (reklam_07). Bu yüzden insan teyidi şart.
Ayrıca üretici v1.2'ye geçti: örnek başına tohum ve kararlı id. Bir şablonu düzeltmek artık diğer şablonların örneklerini
ve inceleme kararlarını değiştirmiyor (doğrulandı: tek şablon değişikliği → yalnızca o şablonun 14 test örneği değişti).

## Golden inceleme · 2. tur (düzeltmelerden sonra)
| | Sonuç |
|---|---|
| Gemini (yeni sohbet, 150 örnek) | 150/150 doğru, 0 işaret |
| İnsan teyidi (Serhat, Gemini'nin "doğru"larından rastgele 20) | 20/20 doğru · insan–LLM uyumu %100 |
| `golden.jsonl` | 297 örnek: 150'si LLM ile denetlenmiş, 20'si insan teyitli, 0 çıkarılan |

**Nasıl okunmalı?** 20 örnekte 0 kaçırma, Gemini'nin kaçırma oranının sıfır olduğunu kanıtlamaz. "Üç kuralı"na göre
%95 güvenle üst sınır ≈ 3/20 = **%15**. 1. turda bulunan hataların hepsi şablon düzeyindeydi (3 şablon) ve düzeltildi.
Bu yüzden kalan etiket hatasının da şablon düzeyinde ve az olması beklenir, ama "sıfır" değil, "düşük ve sınırlı" denmeli.

Teyitte görülen küçük gerçekçilik kusuru: ASCII + BÜYÜK HARF birlikteyken "AKARYAKİTTA" (noktalı İ) çıkıyordu. Türkçe
karaktersiz yazan biri "AKARYAKITTA" yazar. Üretici v1.3 düzeltti. Kararlı tohumlar sayesinde yalnızca bu iki gürültüyü
birlikte taşıyan 4 test örneği değişti (etiketleri aynı, yalnızca harf biçimi).
