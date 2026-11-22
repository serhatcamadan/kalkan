# Olay notu · 2026-11-22 · dış set alıntıları repoya girdi

**Ne oldu:** `eval/results/*__uci.json` ve `*__olta.json` dosyaları (Adım 4'ten beri) commit edilip GitHub'a
gönderildi. Bu dosyalar mesaj metnini (`ham` alanı UCI için zaten çıkarılıyordu) içermiyordu, ama modellerin
**kanıt alıntılarını** içeriyordu: gerçek e-postalardan birebir parçalar (en çok 3 × 80 karakter/mesaj).
PII maskeleme modelden ÖNCE uygulandığı için IBAN / kart / TCKN / telefon / e-posta / tek kullanımlık kod
alıntılarda maskeliydi; isimler ve serbest metin maskeli değildi.

**Etki:** UCI Turkish Spam V01 (CC BY 4.0) ve OLTA-TR zaten herkese açık veri setleri; yeni bilgi açığa çıkmadı.
Ama proje kuralını ihlal etti ("UCI örnek metinleri yayımlanmaz", veri kartı). Bulan: Claude, Adım 8 commit'ini
incelerken (`create mode … ft-0.8b-v3-Q8_0__uci.json`).

**Neden:** Sonuç dosyaları "mesaj metni yok" kuralıyla tasarlandı; alıntıların da mesaj metninin parçası olduğu
gözden kaçtı. `ham` alanı için yapılan istisna `kanitlar`'ı kapsamadı.

**Düzeltme:**
1. `.gitignore`: `eval/results/*__uci.json`, `eval/results/*__olta.json` (yerelde kalır; `make katmanli` ve
   `make yeniden-puanla` onları okur). Metrikler `docs/eval-report.md`'de yayımlanmaya devam eder.
2. Test: `tests/test_veri.py::test_dis_set_sonuclari_repoya_girmez`.
3. Dosyalar takipten çıkarıldı ve **git geçmişinden silindi** (`git filter-repo`), zorla push.

**Ders:** "Metin yok" bir alan listesi değil, bir özelliktir: bir alan mesajdan türetilmiş metin taşıyorsa (alıntı,
özet, hata mesajındaki parça) o da metindir. Yeni sonuç alanları eklenirken bu dosya kontrol listesidir.
