#!/usr/bin/env bash
# KALKAN · VPS sertleştirme (Adım 11a) · Ubuntu 24.04 · root olarak VPS'te çalıştır      v1.1 · 2026-11-22
# v1.1: Ubuntu 24.04 SSH'yi soket etkinleştirmeyle (ssh.socket) çalıştırır: /run/sshd olmadan `sshd -T` hata verir ve
#       v1 bu hatayı gizleyip (2>/dev/null + pipefail) SESSİZCE duruyordu. Artık dizin oluşturulur, hata gösterilir,
#       port soket biriminden de okunur, reload yalnızca servis etkinse yapılır.
# 🧪 bash sertlestir.sh            → önce yalnızca KONTROL eder ve ne yapacağını yazar
#    bash sertlestir.sh --uygula   → uygular
#
# Ne yapar:
#   1. SSH: şifreyle girişi kapatır (yalnızca anahtar). root girişi yalnızca anahtarla (prohibit-password).
#      Ayar /etc/ssh/sshd_config.d/00-kalkan.conf'a yazılır. "00-": sshd bir ayarın İLK değerini kullanır ve
#      dosyaları alfabetik okur; Ubuntu'nun 50-cloud-init.conf'u "PasswordAuthentication yes" diyebilir, 00- onu geçer.
#   2. ufw: gelen her şeyi reddet; yalnızca SSH portu, 80/tcp, 443/tcp, 443/udp açık.
#   3. unattended-upgrades: güvenlik güncellemeleri otomatik.
# Güvenlik kilitleri (kendini kilitleme önlemleri):
#   • root'un authorized_keys'inde en az bir anahtar yoksa DURUR (şifre kapanınca içeri giremezdin).
#   • sshd -t (sözdizimi testi) geçmezse ayar dosyasını geri alır, reload etmez.
#   • Mevcut SSH oturumun KAPANMAZ (reload, restart değil). Yeni girişi başka bir terminalden denemeden bu
#     oturumu kapatma.
set -euo pipefail
UYGULA=0; [[ "${1:-}" == "--uygula" ]] && UYGULA=1
[[ $EUID -eq 0 ]] || { echo "root olarak çalıştır"; exit 1; }
. /etc/os-release; echo "▶ $PRETTY_NAME"

ANAHTAR=/root/.ssh/authorized_keys
SAYI=$(grep -cE '^(ssh-(ed25519|rsa)|ecdsa-|sk-)' "$ANAHTAR" 2>/dev/null || true)
echo "▶ root için kayıtlı SSH anahtarı: ${SAYI:-0}"
[[ "${SAYI:-0}" -ge 1 ]] || { echo "❌ Anahtar yok: şifre kapatılırsa giriş yapamazsın. DURDU."; exit 1; }

mkdir -p /run/sshd && chmod 755 /run/sshd          # soket etkinleştirmede yok olabilir; sshd -T/-t bunu ister
if ! TAM=$(sshd -T 2>&1); then
  echo "❌ sshd -T başarısız:"; echo "$TAM" | sed 's/^/   /'; exit 1
fi
PORT=$(awk '/^port /{print $2; exit}' <<<"$TAM"); PORT=${PORT:-22}
SOKET=$(systemctl show ssh.socket -p Listen --value 2>/dev/null || true)
echo "▶ SSH portu (sshd): $PORT · ssh.socket: ${SOKET:-yok} · servis: $(systemctl is-active ssh 2>/dev/null || true)"
SOKET_PORT=$(grep -oE '[0-9]+ ' <<<"${SOKET##*:} " | head -1 | tr -d ' ' || true)
if [[ -n "$SOKET_PORT" && "$SOKET_PORT" != "$PORT" ]]; then
  echo "⚠️  ssh.socket $SOKET_PORT portunu dinliyor (sshd ayarı $PORT). ufw'de ikisi de açılacak."
fi
echo "▶ Dinleyen SSH: $(ss -tlnH 2>/dev/null | awk '{print $4}' | grep -E ":(${PORT}|${SOKET_PORT:-$PORT})$" | tr '\n' ' ')"
echo "▶ Şu anki etkin SSH ayarları:"
grep -E '^(passwordauthentication|kbdinteractiveauthentication|permitrootlogin|pubkeyauthentication) ' <<<"$TAM" | sed 's/^/   /'
echo "▶ sshd_config.d içeriği:"; ls -1 /etc/ssh/sshd_config.d/ 2>/dev/null | sed 's/^/   /' || true
echo "▶ ufw: $(ufw status 2>/dev/null | head -1 || echo 'kurulu değil')"

if [[ $UYGULA -eq 0 ]]; then
  cat <<EOF

Uygulanacaklar:
  • /etc/ssh/sshd_config.d/00-kalkan.conf:
      PasswordAuthentication no · KbdInteractiveAuthentication no · PermitRootLogin prohibit-password
      PubkeyAuthentication yes · MaxAuthTries 3 · LoginGraceTime 30 · X11Forwarding no
  • ufw: default deny incoming, allow outgoing; allow ${PORT}/tcp, 80/tcp, 443/tcp, 443/udp; enable
  • apt install unattended-upgrades (güvenlik güncellemeleri)
Onaylıyorsan:  bash sertlestir.sh --uygula
EOF
  exit 0
fi

echo "▶ 1/3 SSH"
AYAR=/etc/ssh/sshd_config.d/00-kalkan.conf
YEDEK=""; [[ -f $AYAR ]] && { YEDEK=$(mktemp); cp "$AYAR" "$YEDEK"; }
cat > "$AYAR" <<'EOF'
# KALKAN · Adım 11a · yalnızca anahtarla giriş
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin prohibit-password
PubkeyAuthentication yes
MaxAuthTries 3
LoginGraceTime 30
X11Forwarding no
EOF
chmod 644 "$AYAR"
if ! sshd -t; then
  echo "❌ sshd -t başarısız: ayar geri alınıyor, SSH'ye dokunulmadı."
  if [[ -n $YEDEK ]]; then cp "$YEDEK" "$AYAR"; else rm -f "$AYAR"; fi
  exit 1
fi
# soket etkinleştirmede ssh.service bağlantı gelince başlar ve ayarı o an okur; çalışıyorsa reload (oturumlar kapanmaz)
if systemctl is-active --quiet ssh; then systemctl reload ssh; fi
echo "   etkin ayarlar:"
sshd -T | grep -E '^(passwordauthentication|kbdinteractiveauthentication|permitrootlogin) ' | sed 's/^/   /'

echo "▶ 2/3 ufw"
apt-get install -y -qq ufw >/dev/null
ufw default deny incoming >/dev/null
ufw default allow outgoing >/dev/null
ufw allow "${PORT}/tcp" comment 'SSH' >/dev/null
if [[ -n "${SOKET_PORT:-}" && "$SOKET_PORT" != "$PORT" ]]; then ufw allow "${SOKET_PORT}/tcp" comment 'SSH (soket)' >/dev/null; fi
ufw allow 80/tcp comment 'HTTP (Caddy, sertifika)' >/dev/null
ufw allow 443/tcp comment 'HTTPS (Caddy)' >/dev/null
ufw allow 443/udp comment 'HTTP/3 (Caddy)' >/dev/null
ufw --force enable >/dev/null
ufw status verbose | sed 's/^/   /'

echo "▶ 3/3 otomatik güvenlik güncellemeleri"
apt-get install -y -qq unattended-upgrades >/dev/null
echo 'APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";' > /etc/apt/apt.conf.d/20auto-upgrades
systemctl enable --now unattended-upgrades >/dev/null 2>&1 || true
echo "   $(systemctl is-active unattended-upgrades)"

cat <<EOF

✔ Bitti. BU OTURUMU KAPATMA. Mac'te YENİ bir terminalde dene:
    ssh vps 'echo anahtarla giriş çalışıyor'
  Çalışıyorsa tamam. Çalışmıyorsa bu oturumda:  rm $AYAR && systemctl reload ssh
EOF
