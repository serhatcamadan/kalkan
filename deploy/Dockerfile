# KALKAN · API imajı (Adım 10)                                          v1 · 2026-11-22
# Yalnızca çalışma zamanı: kalkan/ paketi + data/taxonomy.yaml. Eğitim, değerlendirme, veri setleri İMAJA GİRMEZ.
# Paket pip ile kurulmaz (taxonomy.yaml'ı repo köküne göre arar); kaynak /app'te, bağımlılıklar pip ile.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

COPY deploy/requirements-api.txt /tmp/req.txt
RUN pip install -r /tmp/req.txt && rm /tmp/req.txt \
 && useradd --system --uid 10001 --no-create-home kalkan \
 && mkdir -p /app/logs && chown kalkan /app/logs

COPY kalkan ./kalkan
COPY data/taxonomy.yaml ./data/taxonomy.yaml

USER kalkan
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/saglik', timeout=3)"
# Tek süreç: hız sınırı ve kuyruk bellekte (birden çok işçi sınırı böler). Erişim logu: yalnızca yol + durum kodu.
# --proxy-headers YOK: istemci IP'si yalnızca kalkan.api'de, KALKAN_GUVENILIR_VEKIL=1 iken X-Forwarded-For'dan okunur.
CMD ["uvicorn", "kalkan.api:uygulama", "--factory", "--host", "0.0.0.0", "--port", "8000", \
     "--workers", "1", "--no-proxy-headers", "--no-server-header"]
