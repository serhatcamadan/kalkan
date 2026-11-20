"""KALKAN · Adım 2 · çıktı biçimi kaç token? (llama-server /tokenize)   v1 · 2026-11-19
👀 İsteğe bağlı ama öğretici: Adım 1 dersi "gecikme = üretilen token" idi. Bu script aynı cevabı
girintili / kompakt / kompakt+kısa alıntı biçimlerinde Qwen3.5 tokenizer'ıyla sayar ve VPS'te
ölçülen üretim hızlarıyla (0.8B 22 tok/s, 2B 12.8 tok/s) süre tahmini yapar.

Kullanım (Mac, repo kökünde):
  python3 tools/token_olc.py --server .spike/llama.cpp/build/bin/llama-server --model .spike/gguf/C-Q4_K_M.gguf
"""
import argparse
import json
import subprocess
import time
import urllib.request

ORNEK = {"kanitlar": [
    {"alinti": "Mavibank hesabınız şüpheli işlem nedeniyle askıya alınmıştır.", "sinyal": "kurum_taklidi"},
    {"alinti": "2 saat içinde hxxps://mavibank-guvenlik[.]top adresinden kimlik bilgilerinizi doğrulamazsanız",
     "sinyal": "kimlik_talebi"},
    {"alinti": "kartınız iptal edilecektir", "sinyal": "aciliyet"}], "tur": "kurum_taklidi"}
KISA = {"kanitlar": [
    {"alinti": "hesabınız şüpheli işlem nedeniyle askıya alınmıştır", "sinyal": "kurum_taklidi"},
    {"alinti": "kimlik bilgilerinizi doğrulamazsanız", "sinyal": "kimlik_talebi"},
    {"alinti": "2 saat içinde", "sinyal": "aciliyet"}], "tur": "kurum_taklidi"}
BICIMLER = {
    "girintili (Adım 1'de modelin yazdığı)": json.dumps(ORNEK, ensure_ascii=False, indent=2),
    "kompakt": json.dumps(ORNEK, ensure_ascii=False, separators=(",", ":")),
    "kompakt + kısa alıntı (hedef)": json.dumps(KISA, ensure_ascii=False, separators=(",", ":")),
    "kompakt, ensure_ascii=True (\\u kaçışlı)": json.dumps(KISA, separators=(",", ":")),
}


def post(url, body):
    req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=60).read())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--port", type=int, default=8099)
    a = ap.parse_args()
    p = subprocess.Popen([a.server, "-m", a.model, "--port", str(a.port), "-c", "512"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    url = f"http://127.0.0.1:{a.port}"
    try:
        for _ in range(100):
            try:
                if urllib.request.urlopen(url + "/health", timeout=1).status == 200:
                    break
            except Exception:  # noqa: BLE001
                time.sleep(0.3)
        print(f"| biçim | karakter | token | VPS 0.8B sn | VPS 2B sn |\n|---|---|---|---|---|")
        for ad, s in BICIMLER.items():
            n = len(post(url + "/tokenize", {"content": s})["tokens"])
            print(f"| {ad} | {len(s)} | {n} | {n / 22:.1f} | {n / 12.8:.1f} |")
    finally:
        p.terminate()


if __name__ == "__main__":
    main()
