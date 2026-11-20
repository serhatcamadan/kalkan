"""KALKAN · Adım 3 · dış veri setlerini indir (repoya KONMAZ)        v1 · 2026-11-20
🧪 KESİN DENE (Mac):  python data/external/download.py

1) OLTA-TR — sentetik Türkçe oltalama e-postaları, Zenodo, CC BY 4.0, DOI 10.5281/zenodo.19472163
   ⚠️ Oltalama örneklerinin ~%13'ü URLhaus'tan GERÇEK zararlı URL içeriyor. Bu script tüm URL'leri
   indirme anında DEFANG eder (http→hxxp, ilk nokta→[.]). Linkler asla açılmaz.
2) UCI Turkish Spam V01 — 826 e-posta, CC BY 4.0, DOI 10.24432/C5WG7F
   ⚠️ "Birkaç kişisel hesaptan toplanmış" GERÇEK e-postalar. Yalnızca toplu metrik için kullanılır:
   örnek metinleri rapora, README'ye, loga YAZILMAZ; repoya konmaz.

Çıktı: data/external/olta_tr.jsonl, data/external/uci_trspam.jsonl  (alanlar: kaynak, etiket, metin)
Etiketler ikili: dolandiricilik | degil  (bizim 11 türümüzle bire bir eşlenmez → Adım 8'de ikili değerlendirme)
"""
import csv
import hashlib
import io
import json
import re
import urllib.request
import zipfile
from pathlib import Path

BURASI = Path(__file__).resolve().parent
OLTA = {
    "phishing.csv": ("https://zenodo.org/records/19472163/files/phishing.csv?download=1", "422006159092ef69d129d1f3c9ec0032"),
    "legitimate.csv": ("https://zenodo.org/records/19472163/files/legitimate.csv?download=1", "7f8ae5b70a8cdaaa06838d39bdd9c663"),
}
UCI_ZIP = "https://archive.ics.uci.edu/static/public/530/turkish+spam+v01.zip"
csv.field_size_limit(10_000_000)


def indir(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "kalkan-portfolio/0.3"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def defang(t: str) -> str:
    def f(m):
        u = m.group(0).replace("https://", "hxxps://").replace("http://", "hxxp://")
        return re.sub(r"\.", "[.]", u, count=1)
    return re.sub(r"https?://[^\s\"'<>]+", f, t)


def olta() -> int:
    n = 0
    with open(BURASI / "olta_tr.jsonl", "w", encoding="utf-8") as out:
        for ad, (url, md5) in OLTA.items():
            veri = indir(url)
            assert hashlib.md5(veri).hexdigest() == md5, f"{ad}: md5 tutmuyor (dosya değişmiş olabilir)"
            for row in csv.DictReader(io.StringIO(veri.decode("utf-8-sig"))):
                metin = defang(row.get("email_with_url") or row.get("email_without_url") or "")
                if not metin.strip():
                    continue
                out.write(json.dumps({"kaynak": "olta_tr", "etiket": "dolandiricilik" if ad == "phishing.csv" else "degil",
                                      "sektor": row.get("sector"), "kategori": row.get("category"),
                                      "metin": metin}, ensure_ascii=False) + "\n")
                n += 1
    return n


def uci() -> int:
    z = zipfile.ZipFile(io.BytesIO(indir(UCI_ZIP)))
    ad = next(n for n in z.namelist() if n.lower().endswith(".csv"))
    ham = z.read(ad)
    for kod in ("utf-8-sig", "cp1254", "iso-8859-9"):
        try:
            metin = ham.decode(kod)
            break
        except UnicodeDecodeError:
            continue
    n = 0
    with open(BURASI / "uci_trspam.jsonl", "w", encoding="utf-8") as out:
        for row in csv.reader(io.StringIO(metin)):
            if len(row) < 2 or row[-1].strip().lower() not in ("spam", "ham", "normal"):
                continue
            out.write(json.dumps({"kaynak": "uci_trspam", "etiket": "spam" if row[-1].strip().lower() == "spam" else "degil",
                                  "metin": defang(",".join(row[:-1]))}, ensure_ascii=False) + "\n")
            n += 1
    return n


if __name__ == "__main__":
    print("OLTA-TR:", olta(), "satır")
    try:
        print("UCI Turkish Spam:", uci(), "satır")
    except Exception as e:  # noqa: BLE001
        print("UCI indirilemedi:", e, "\n  → Elle: https://archive.ics.uci.edu/dataset/530 → trspam.csv'yi data/external/ altına koy")
