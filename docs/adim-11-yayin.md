# Adım 11 — VPS'e yayın: sertleştirme, Docker, Caddy + HTTPS · v1 · 2026-11-22

## Aşamalar (her biri bir öncekini doğruladıktan sonra)
| | Ne | Doğrulama |
|---|---|---|
| 11a | SSH yalnızca anahtar, ufw (SSH/80/443), otomatik güvenlik güncellemeleri (`deploy/sertlestir.sh`) | Yeni terminalden `ssh vps` çalışıyor; şifreyle giriş reddediliyor |
| 11b | DuckDNS alt alan adı → VPS IP | `dig +short <ad>.duckdns.org` VPS IP'sini veriyor |
| 11c | Docker Engine + compose; yalnızca çalışma zamanı dosyaları `make vps-gonder` ile (git/veri/eğitim sunucuya gitmez) | `curl 127.0.0.1:8000/saglik` → model ok |
| 11d | Caddy + Let's Encrypt | `https://<ad>.duckdns.org` açılıyor; HTTP → HTTPS; sertifika geçerli |

## Kararlar
- **Alan adı: DuckDNS** (ücretsiz; hesap başına 5 alt alan adı). VPS IP'si sabit olduğu için güncelleyici
  (cron/konteyner) gerekmez. Bilinen bedel: duckdns.org bazı DNS engel listelerinde "dinamik DNS" kategorisinde;
  bazı kurumsal ağlar açmayabilir. Kalıcı bir yayın için kendi alan adı önerilir (README).
- **Sunucuya git klonu yok:** `make vps-gonder` yalnızca `kalkan/`, `data/taxonomy.yaml` ve `deploy/` çalışma dosyalarını
  rsync ile gönderir. Sunucuda repo geçmişi, veri setleri, eğitim kodu, GitHub kimlik bilgisi bulunmaz.
- **SSH:** şifre kapalı, root yalnızca anahtarla (`prohibit-password`). Ayrı sudo kullanıcısı bu adımda yok (tek kişilik
  demo sunucusu; kendini kilitleme riski > kazanç). Ayar `sshd_config.d/00-kalkan.conf`: sshd bir ayarın ilk değerini
  kullandığı için `50-cloud-init.conf`'un "PasswordAuthentication yes"ini geçer.
- **Docker ve ufw:** Docker yayınlanan portlarda ufw kurallarını atlar. Bu yüzden API host'ta yalnızca `127.0.0.1:8000`,
  llama-server hiç yayınlanmaz; dışarıya yalnızca Caddy'nin 80/443'ü açık (ufw'de de açık, çelişki yok).
- **Caddy:** `caddy:2.11` resmi imaj; yönetim API'si kapalı (`admin off`); istek gövdesi en çok 64 KB; HSTS; erişim
  logu kapalı (IP tutulmaz). İstemcinin `X-Forwarded-For`'u aktarılmaz, Caddy kendi gördüğü adresi yazar; API bu
  başlığın **son** öğesini okur (v1.1; ilk öğe istemcinin yazabildiği değer olabilirdi, testli).
- **Sabit sürümler:** llama.cpp commit `5812201a8` (build 12544, Mac ve VPS ölçümleriyle aynı), Caddy `2.11`, Python `3.11-slim`.
- **llama imajı kaynaktan (`deploy/Dockerfile.llama`):** Adım 10'da varsaydığım resmi `ghcr.io/ggml-org/llama.cpp:server-b12544`
  etiketi **yok** (A3'teki tek risk gerçekleşti). Sürümü değiştirmek bütün ölçümleri geçersiz kılardı; bunun yerine aynı
  commit derleniyor. CPU hedefi AVX2 tabanı (`GGML_NATIVE=OFF`): sağlayıcı VM'i AVX2'li E5-2699v4'ten AVX-512'li
  Platinum 8260'a taşıdı; yerel (native) derleme AVX-512 kullanır ve geri taşınırsa SIGILL ile çöker. Adım 1
  benchmark'ı AVX2'li makinede yapıldığı için ölçülen komut setiyle de aynı.

## Tahminler
| # | Tahmin |
|---|---|
| Y1 | 11a ilk denemede sorunsuz; `sshd -T` → passwordauthentication no |
| Y2 | Docker imajları ~3–5 dk'da iner/derlenir; `llama` 20–40 sn'de sağlıklı |
| Y3 | Let's Encrypt sertifikası ilk istekte ≤ 60 sn'de alınır |
| Y4 | HTTPS üzerinden p95 ≈ VPS bench (≤ 8 sn); arayüzde üç örnek Mac'teki kararlarla aynı |

## Sonuçlar (2026-11-22/23) · **https://kalkan-serhat.duckdns.org**
| Kontrol | Sonuç |
|---|---|
| SSH anahtarla | ✅ "anahtarla giriş çalışıyor" |
| SSH şifreyle | ✅ `Permission denied (publickey)`, şifre sorulmadı |
| `sshd -T` | passwordauthentication no · permitrootlogin without-password |
| ufw | aktif; yalnızca 22/tcp, 80/tcp, 443/tcp, 443/udp (v4+v6) |
| Docker | 29.10.0 · Compose v5.8.0 |
| llama imajı | kaynaktan, commit 5812201a8, AVX2; konteyner healthy |
| API (VPS içi) | sağlık `model: ok`; gümrük mesajı → yüksek, sahte_kargo_gumruk (Mac ile aynı karar ve katman deseni: kural yüksek, model düşük) |
| Let's Encrypt | HTTP-01, 7 farklı doğrulama noktası; hesap kaydından sertifikaya **~5 sn** |
| HTTP → HTTPS | ✅ 308 → https |
| HTTPS | ✅ HTTP/2 (+ h3 alt-svc), CSP ve no-store başlıkları Caddy'den geçiyor |
| 8000 / 8080 dışarıdan | ✅ ikisi de zaman aşımı (curl 28): API ve model internetten doğrudan erişilemez |

**Karne:** Y1 ✅ · Y2 ◐ (llama imajı hazır etiket yerine kaynaktan; derleme ~10 dk) · Y3 ✅ (5 sn) · Y4 Adım 12'de
(HTTPS üzerinden p95 ölçümü).

**Notlar:**
- `curl -I` (HEAD) ana sayfada **405** döndü: FastAPI `@app.get` HEAD'i kabul etmiyor. Tarayıcılar GET kullandığı için
  arayüzü etkilemiyor; ama çalışma süresi izleyicileri çoğunlukla HEAD gönderir → Adım 12 temizliği (`/` ve `/saglik`
  için HEAD).
- Caddy uyarıları zararsız: `header_up X-Forwarded-For` "gereksiz" (varsayılan zaten aynı; açık yazılı tutuldu, API
  ayrıca son öğeyi okuyor) ve QUIC alıcı tamponu küçük (düşük trafikte etkisiz; istenirse `sysctl net.core.rmem_max`).
- VPS'teki ilk analiz 3,0 sn (soğuk önbellek); p95 Adım 12'de HTTPS üzerinden ölçülecek.
