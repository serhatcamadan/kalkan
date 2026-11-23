# Adım 12 — temizlik, uzak ölçüm, README, rapor, video · v1 · 2026-11-23

## 12a — temizlik ve yayındaki sistemin ölçümü
| Konu | Değişiklik |
|---|---|
| HEAD isteği 405 (Adım 11) | `/` ve `/saglik` GET + HEAD (`api.py` v1.2); test |
| Starlette `httpx` uyarısı | geliştirme bağımlılığı `httpx2>=2.16,<3` (Starlette 1.7 artık onu arıyor); uyarı kalkar |
| Üst üste binen kanıtlar (Adım 11 notu) | arayüz çakışan aralıkları tek işarette birleştirir, numaralar "1,2" (`kalkan.js` v1.1); liste aynen kalır |
| Uzak gecikme (Y4) | `deploy/uzak_olcum.py`: test bölümünden sabit tohumlu 20 mesaj, HTTPS, istekler arası 6,5 sn (hız sınırı), duvar saati + sunucu süresi, ilk (soğuk) istek ayrı |
| Sürüm | 0.10.1 |

### Tahmin (Y4)
Duvar p95 ≈ sunucu p95 + 100–300 ms (TLS + Türkiye içi ağ); sunucu p95 ≤ 8 sn (VPS bench 7,4 sn); 20/20 durum 200;
alarm kararları golden etiketleriyle ≥ 19/20 tutarlı.

### Sonuçlar (Mac → https://kalkan-serhat.duckdns.org, 20 mesaj, 2026-11-23)
| | p50 | p95 | en çok |
|---|---|---|---|
| duvar saati (ağ + TLS + analiz), ilk istek hariç 19 | 5,61 sn | **6,94 sn** | 7,47 sn |
| sunucu (yalnızca analiz) | 5,47 sn | 6,81 sn | – |
| ilk istek (soğuk) | 4,52 sn | | |

- Durum kodları: 20/20 **200**. Alarm kararı golden etiketiyle tutarlı: **20/20**.
- Ağ + TLS payı ≈ **140 ms** (duvar − sunucu).
- Gecikme çıktı uzunluğuyla gidiyor: meşru mesajlar (kanıtsız kısa JSON) **1,4–2,0 sn**, dolandırıcılık (2–3 alıntılı)
  **4–7 sn**. Kullanıcı açısından hoş bir asimetri: "sorun yok" hızlı, uyarı biraz daha uzun.
- **Karne:** Y4 ✅ (sunucu p95 6,8 ≤ 8 sn; fark 100–300 ms aralığında; 20/20 ≥ 19/20). n=19'da p95 fiilen en yavaş
  ikinci istek; kaba bir tahmin.
