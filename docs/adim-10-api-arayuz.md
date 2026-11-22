# Adım 10 — API, demo arayüzü, docker compose · v1 · 2026-11-22

## Ne var
| Parça | Dosya | Not |
|---|---|---|
| API | `kalkan/api.py` (FastAPI 0.162, uvicorn 0.54; sürümler 2026-11-22 PyPI) | `POST /analiz` ürün yolu (ADR-0006), `GET /saglik`, `GET /` arayüz. OpenAPI/docs kapalı. |
| Arayüz | `kalkan/web/{index.html,kalkan.css,kalkan.js}` | Tek sayfa, dış kaynak yok, satır içi kod yok (CSP `script-src 'self'`). |
| İmaj | `deploy/Dockerfile`, `deploy/requirements-api.txt` | Yalnızca `kalkan/` + `data/taxonomy.yaml`; root olmayan kullanıcı. |
| Compose | `deploy/compose.yaml`, `deploy/.env.ornek` | `llama` (resmi llama.cpp imajı, **server-b12544** = spike/bench ile aynı derleme) + `api`. |

## Tasarım kararları
- **Arayüzün ana fikri "kanıt önce":** sonuç bir rozet değil, mesajın kendisi; modelin/kuralın kapıdan geçen
  alıntıları mesaj balonunun üzerinde işaretlenir, altında numaralı açıklama. Gösterilen metin **maskeli**
  (IBAN, kart, telefon, kod → `[IBAN]` …); kanıt aralıkları bu metne göre, API testinde doğrulanıyor.
- **Dil:** karar cümlesi politikadan gelir ("güvenli" asla yazılmaz, ADR-0004). Düşük risk "Düşük risk / Belirgin
  bir dolandırıcılık işareti bulunamadı" olarak gösterilir, altında "emin değilseniz resmi kanaldan arayın".
- **XSS:** kullanıcı metni DOM'a yalnızca `textContent`/`append` ile girer; test JS'te `.innerHTML` olmadığını denetler.
- **Hız sınırı:** IP başına dakikada 10, günde 200 (ortamdan ayarlı). IP, yalnızca `KALKAN_GUVENILIR_VEKIL=1` iken
  `X-Forwarded-For`'dan; uvicorn'un `--proxy-headers`'ı bilerek kapalı (tek mekanizma). Test: başlık taklidiyle
  sınır aşılamıyor.
- **Kuyruk:** llama-server tek yuvalı → aynı anda 1 model çağrısı, en çok 4 bekleyen; fazlası anında 503.
  VPS p95 7,4 sn → kuyruğun sonundaki istek ~37 sn bekleyebilir; bekleme tavanı 30 sn (sonra 503).
- **Model düşerse:** API 200 döner, sonuç fail-closed (kural orta/yüksek → o; aksi halde "Değerlendirilemedi")
  ve arayüz "Dil modeli bu kontrolde yanıt vermedi" uyarısı gösterir.
- **Compose sertleştirme:** iki konteyner de salt okunur kök, tüm yetenekler düşürülmüş, `no-new-privileges`,
  bellek tavanı (llama 2 GB, api 512 MB), log döndürme. llama-server dışarıya hiç açılmaz; API yalnızca
  `127.0.0.1:8000` (internete Caddy açacak, Adım 11).
- **Demo örnekleri:** gümrük ücreti (yüksek), kargo bildirimi (düşük), yakın taklidi (yüksek). Meşru OTP örneği
  bilerek yok: kuralın bilinen yanlış alarmı (Adım 9, kor_17); README "Sınırlar"da.

## Testler (`tests/test_api.py`, 11)
Ürün yolu + kanıt aralıkları, PII maskesi, model yokken fail-closed 200, girdi sınırları (boş/10.001/ek alan/düz
metin), dakika sınırı + Retry-After, kayan pencere, XFF taklidi, kuyruk doluyken 503, güvenlik başlıkları + satır
içi kod yok + docs kapalı, sağlık, denetim satırında mesaj yok.

## Tahminler (Mac'te gerçek llama-server ile)
| # | Tahmin |
|---|---|
| A1 | `make api-deneme`: gümrük mesajı → yüksek, sahte_kargo_gumruk, ~0,7–1,5 sn |
| A2 | Arayüzde üç örneğin kararları CLI ile aynı; tarayıcı konsolunda CSP hatası yok |
| A3 | Docker compose VPS'te (Adım 11) ilk denemede ayağa kalkar; tek risk llama imaj etiketinin varlığı |

## Sonuçlar (Mac, gerçek llama-server, ft-v3 Q8_0)
- `make test`: 114 passed (tek uyarı: Starlette TestClient için `httpx` yerine `httpx2` öneriyor; Adım 12 temizliği).
- `make api-deneme`: sağlık `model: ok`; gümrük mesajı → **yüksek**, sahte_kargo_gumruk, **209 ms**; boş mesaj → 422;
  denetim satırı mesajdan kelime içermiyor.
- Arayüz gerçek modelle: kanıtlar doğru aralıkta işaretli (ödeme cümlesi ve bağlantı), karar ve öneri okunur.

**Karne:** A1 ◐ (karar ve tür ✅; süre tahmini ❌, aşağıda) · A2 ✅ · A3 Adım 11'de.

**Gerçek bir katman vakası:** denetim satırı `kural_risk: yuksek`, `model_risk: dusuk`, 198 ms. Model bu açık
gümrük mesajını **meşru** saydı (kısa `{"kanitlar":[],"tur":"mesru_islem"}` cevabı: süre bu yüzden 0,2 sn).
Kural yüksek dedi, model riski düşüremediği için karar yüksek kaldı; ekrandaki kanıtlar kuraldan. Olası neden:
"Kestane Kargo" adversarial marka havuzunda, model eğitimde hiç görmedi. Katmanlı tasarımın (ADR-0006) ve metinsiz
denetim kaydının neden var olduğunun canlı örneği; model tek başına çalışsaydı bu mesaj "düşük" alırdı.
