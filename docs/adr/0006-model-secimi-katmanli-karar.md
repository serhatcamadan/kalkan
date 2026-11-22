# ADR-0006: Model seçimi: kural birinci katman, ince ayarlı 0.8B (Q8_0) ikinci görüş

- **Durum:** Kabul edildi · 2026-11-22
- **İlgili:** ADR-0001 (dönüşüm yolu), ADR-0002 (llama-server), ADR-0005 (politika), `docs/adim-07-finetune.md`,
  `docs/adim-08-gguf-eval.md`

## Bağlam
Karar kuralı (Adım 5'te konuldu): golden'da dolandırıcılık recall ≥ 0.95, meşru FPR ≤ 0.05, kapı öncesi kanıt
geçerliliği ≥ 0.95, adversarial sızıntı 0, VPS p95 ≤ 15 sn → geçenler arasında en ucuz. Sert kısıt: banka modu yerel.

Adaylar ve golden sonuçları (tam sistem: şema + kapı + politika v1.1):

| aday | makro-F1 | recall | FPR | sızıntı | yer / maliyet | kural? |
|---|---|---|---|---|---|---|
| kural | 0.887 | 0.975 | 0.000 | 1* | yerel, $0 | ❌ sızıntı |
| TF-IDF (şablon v1.4) | 0.689 | 1.000 | 0.000 | 3 | yerel, $0 | ❌ sızıntı, kanıt yok |
| zero-shot 2B | 0.236 | – | 0.43 | – | yerel | ❌ |
| ft-0.8b-v2 (Q8_0) | 0.507 | 1.000 | 0.296 | 0 | yerel | ❌ FPR |
| ft-0.8b-v3 (Q8_0) | 0.552 | 1.000 | 0.019 | 1 | yerel | ❌ sızıntı |
| gpt-5.4-mini (BYOK) | 0.905 | ✅ | 0.000 | 0 | bulut, ~$0.0012/mesaj | ✅, ama banka modunda yasak |
| **★ katmanlı: kural + ft-0.8b-v3 (Q8_0)** | **0.905** | **1.000** | **0.018** | **0** | **yerel, $0** | **✅** |

\* Kuralın sızıntısı tür vekiliyle 1, politika v1.1'den geçince 0. Tabloda Adım 4 rapor değeri.

VPS (4 vCPU Xeon Platinum 8260, 6 GB, Q8_0, üretim istemi + şeması, 384 token, 20 koşu): p95 **6,2 sn** (önbellekli),
**7,4 sn** (önbelleksiz); JSON %100, kesilme %0; RSS 1,08 GB, boş RAM ≥ 4,9 GB. ✅

## Karar
1. **Birinci katman: kural + deterministik sinyaller + politika (ADR-0005).** Türü ve taban riski verir.
2. **İkinci görüş: ince ayarlı Qwen3.5-0.8B, LoRA v3 (it450), GGUF Q8_0, llama-server.** Kural "düşük" dediğinde,
   model dolandırıcılık türü + kapıdan geçen ≥ 2 kanıt + bunlardan en az biri ödeme/kod/kimlik talebi üretirse risk
   **ORTA**'ya çıkar. Model riski **asla düşüremez**. Modelin kapıdan geçen alıntıları her durumda "Neden?" açıklaması.
   Varyant (`ikinci_talep`) golden görülmeden önce seçildi (`eval/katmanli.py`).
3. **Nicemleme Q8_0, Q4_K_M değil.** Q4 doğrulamada tür doğruluğunu −0.091 düşürdü ve bir dolandırıcılık şablonunu
   meşruya kaydırdı; Q8 MLX ile 0.985 uyumlu. Q4 VPS'te ~%25 hızlı, ama Q8 zaten hedefin yarısının altında.
4. **gpt-5.4-mini BYOK isteğe bağlı mod olarak kalır** (banka modu dışında, kullanıcının anahtarıyla).
5. **Kapsam: SMS/WhatsApp.** E-postada (OLTA, UCI) model neredeyse her şeye alarm veriyor; README'de "e-posta için
   uygun değil" sınırı.

## Neden bu, alternatifler değil
- **Yalnızca kural:** golden'da güçlü ama doğrulamada 0.990 → 0.722 (yeni şablonlarda) ve OLTA'da ayırt +0.096 →
  kurallar yazıldıkları şablon diline bağlı. Katmanlı OLTA'da +0.122 ve golden'da recall 0.975 → 1.000.
- **Yalnızca ft-v3:** recall/FPR geçiyor ama tür F1 0.552 ve 1 sızıntı; tür ve taban risk için kural daha güvenilir.
- **gpt-5.4-mini:** eşit kalite, ama mesaj dışarı çıkar (banka modu yasak) ve maliyetli.
- **2B ince ayar:** v3 kuralı geçtiği için gereksiz; ~2,5× eğitim süresi.

## Bedeli ve açık riskler
- **FPR tahmini zayıf:** 54 meşru mesajda 1 yanlış alarm; %95 Wilson aralığı ≈ [0.003, 0.098]. Üst sınır 0.05'in
  üstünde. Gerçek, izinli meşru SMS örnekleriyle daraltılmalı (açık iş).
- **Golden sentetik ve aynı elden:** kurallar, şablonlar ve golden aynı yazardan. Gerçek dağılım vekili (OLTA)
  e-posta; SMS için bağımsız, gerçek bir değerlendirme seti yok (açık iş).
- **Kapı anlamı doğrulamaz:** alıntının mesajda geçtiğini doğrular, etiketin (ör. `kod_talebi`) doğru olduğunu değil.
  Adım 8b'de v2 meşru onay kodlarını "kod talebi" diye alıntıladı; v3'te sınıf dengesiyle büyük ölçüde düzeldi.
  Kalıcı çözüm değil; ADR-0005'e not.
- **Model türü hâlâ zayıf** (doğrulama 0.64): dolandırıcılık türleri arası karışma. Kullanıcıya gösterilen tür
  kuraldan geldiği için etkisi sınırlı; ama kural "düşük" deyip model yükselttiğinde gösterilen tür modelin türüdür.
- **Hız ölçümü yeni donanımda:** VPS, Adım 1'deki E5-2699 v4'ten Xeon Platinum 8260'a taşınmış (sağlayıcı). Adım 1
  sayılarıyla doğrudan kıyaslanamaz.
- **İki sistem bakımı:** kural ve model ayrı ayrı güncellenmeli; katmanlı değerlendirme (`make katmanli`) her
  değişiklikte yeniden koşar ($0).

## Uygulama
`kalkan/service.py` şu an yalnızca model yolunu çalıştırıyor. Katmanlı karar Adım 9'da servise taşınacak:
`eval/katmanli.py`'deki `birlestir("ikinci_talep", …)` mantığı `kalkan/policy.py`'ye, kural modeli
`eval/modeller/kural.py`'den `kalkan/`'a. Davranış, değerlendirmeyle aynı kodu paylaşır (ölçülen = çalışan).
