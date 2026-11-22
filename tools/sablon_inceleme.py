"""KALKAN · Adım 7b · yeni şablonların LLM ön-incelemesi (Gemini)       v1.1 · 2026-11-22

Golden incelemesinin (tools/llm_inceleme.py) şablon düzeyindeki karşılığı: hata ŞABLONDA ise her örneğe yayılır,
o yüzden örnek değil şablon incelenir. Her yeni şablon (v1.3, numara ≥ 08) için 2 üretilmiş örnek gösterilir.
Veri tamamen sentetiktir. ⚠️ data/external/ ASLA bu yolla dışarı gönderilmez.

1) python tools/sablon_inceleme.py disari  → data/templates/inceleme/paket.md   (Gemini'ye yükle)
   Cevabı data/templates/inceleme/cevap.json olarak kaydet.
   --ilk 15 → yalnızca numarası ≥ 15 olan şablonlar (Adım 8c: yeni meşru/reklam)
2) python tools/sablon_inceleme.py iceri [--ilk 15]   → kararlar.jsonl + işaretlenenlerin listesi (insan bunlara bakar)
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))
from kalkan.taxonomy import yukle  # noqa: E402

DIZIN = KOK / "data/templates/inceleme"
PAKET, CEVAP, KARAR = DIZIN / "paket.md", DIZIN / "cevap.json", DIZIN / "kararlar.jsonl"
ILK_YENI = 8

YONERGE = """# Görev: Türkçe dolandırıcılık SMS ŞABLONLARININ denetimi

Sen bağımsız bir veri denetçisisin. Aşağıda {n} SENTETİK mesaj şablonu var; her biri için şablondan üretilmiş
2 örnek gösteriliyor. Bu şablonlardan küçük bir dil modeli eğitilecek. Hata şablondaysa YÜZLERCE örneğe yayılır,
bu yüzden ŞABLONU değerlendir. Kurum/marka adları, numaralar ve linkler UYDURMADIR.

## Her şablon için sırayla sor; "evet" dediğin İLK soruda karar ver
1. Gerçek hayatta böyle bir SMS/WhatsApp mesajı gelmesi akla yatkın DEĞİL mi (anlamca çelişkili, saçma)? → "cikar"
2. Tür AÇIKÇA yanlış mı, ya da mesaj BAŞKA bir türe en az bu kadar uyuyor mu? → "tur" (+ yeni_tur)
3. Türkçe dil hatası var mı (ek uyumu, çekim, anlam bozukluğu), ya da bir kanıt alıntısı yanındaki sinyalle
   AÇIKÇA uyuşmuyor mu, ya da ANA dolandırıcılık hamlesi kanıtlarda hiç yok mu? → "duzelt" (+ oneri)
4. Hiçbiri değilse → "dogru"

## Önemli kurallar
- Emin değilsen "dogru". Sadece AÇIK sorunları işaretle.
- BİLİNÇLİ gürültü hata DEĞİLDİR: Türkçe karaktersiz yazım, yazım hatası, BÜYÜK HARF, emoji, çift boşluk,
  [TEL] [IBAN] [OTP] [KART] maske etiketleri, "Ahmet Hanım" gibi rastgele ad-hitap eşleşmesi (bilinen, kapsam dışı).
- reklam_spam ve mesru_islem şablonlarında kanıt listesinin BOŞ olması doğrudur.
- Bazı şablonlar BİLEREK sınıflar arası tuzaktır: "kargo bedava" diyen reklam, şubede bekleyen gerçek kargo
  bildirimi, kod içeren meşru mesaj. Bunlar meşru/reklam ise doğrudur; dolandırıcılığa benzemeleri amaçlanmıştır.
- En fazla 3 kanıt seçilebilir; küçük ayrıntıların eksikliği hata değildir.

## Türler
{turler}

## Sinyaller
{sinyaller}

## Çıktı biçimi (YALNIZCA geçerli bir JSON dizisi, başka metin yok; her şablon için tam bir öğe)
[{{"id": "kargo_08", "karar": "dogru"}},
 {{"id": "kurum_09", "karar": "tur", "yeni_tur": "odul_kampanya", "not": "kısa gerekçe"}},
 {{"id": "gorev_10", "karar": "duzelt", "not": "kısa gerekçe", "oneri": "düzeltilmiş cümle"}},
 {{"id": "oyun_11", "karar": "cikar", "not": "kısa gerekçe"}}]
"karar" ∈ dogru | tur | duzelt | cikar. "dogru" dışındaki her kararda "not" zorunlu.

## Şablonlar
"""


def yeni_mi(sid: str) -> bool:
    return int(sid.rsplit("_", 1)[1]) >= ILK_YENI


def ornekler() -> dict[str, list[dict]]:
    """Her yeni şablon için 2 örnek: gürültüsüz biri + (varsa) gürültülü biri."""
    grup = defaultdict(list)
    for sp in ("egitim", "dogrulama"):
        for x in open(KOK / f"data/splits/{sp}.jsonl", encoding="utf-8"):
            r = json.loads(x)
            if yeni_mi(r["sablon_id"]):
                grup[r["sablon_id"]].append(r)
    out = {}
    for sid, rows in sorted(grup.items()):
        rows.sort(key=lambda r: r["id"])
        temiz = [r for r in rows if not r["gurultu"]]
        kirli = [r for r in rows if r["gurultu"]]
        out[sid] = (temiz[:1] + kirli[:1] + temiz[1:2])[:2]
    return out


def disari() -> None:
    tax = yukle()
    turler = "\n".join(f"- {t['id']}: {t['tanim']} AYIRT EDİCİ: {t['ayirt_edici']}" for t in tax["turler"])
    sinyaller = "\n".join(f"- {s['id']}: {s['tanim']}" for s in tax["sinyaller"])
    sec = ornekler()
    parca = [YONERGE.format(n=len(sec), turler=turler, sinyaller=sinyaller)]
    for sid, rows in sec.items():
        parca.append(f"### {sid}\nTÜR: {rows[0]['tur']}")
        for j, r in enumerate(rows, 1):
            k = "\n".join(f"    - {x['sinyal']}: \"{x['alinti']}\"" for x in r["hedef"]["kanitlar"]) or "    (yok)"
            parca.append(f"ÖRNEK {j}: {r['model_girdisi']}\n  KANITLAR:\n{k}")
        parca.append("")
    DIZIN.mkdir(parents=True, exist_ok=True)
    PAKET.write_text("\n".join(parca), encoding="utf-8")
    print(f"{PAKET.relative_to(KOK)}  ({len(sec)} şablon, {PAKET.stat().st_size // 1024} KB)")


def iceri() -> None:
    ham = re.sub(r"^```(json)?|```\s*$", "", CEVAP.read_text(encoding="utf-8").strip(), flags=re.M).strip()
    cevap = json.loads(ham)
    beklenen = set(ornekler())
    turler = {t["id"] for t in yukle()["turler"]}
    temiz, sorun = [], []
    for d in cevap:
        ok = d.get("id") in beklenen and d.get("karar") in ("dogru", "tur", "duzelt", "cikar")
        ok = ok and (d["karar"] != "tur" or d.get("yeni_tur") in turler)
        (temiz if ok else sorun).append(d)
    with open(KARAR, "w", encoding="utf-8") as f:
        for d in temiz:
            f.write(json.dumps({**d, "kaynak": "llm"}, ensure_ascii=False) + "\n")
    print(f"karar: {len(temiz)}/{len(beklenen)} · {dict(Counter(d['karar'] for d in temiz))}")
    for d in temiz:
        if d["karar"] != "dogru":
            ek = f" → {d['yeni_tur']}" if d["karar"] == "tur" else (f"\n      öneri: {d['oneri']}" if d.get("oneri") else "")
            print(f"  ⚑ {d['id']:11s} {d['karar']}{ek}\n      not: {d.get('not', '')}")
    if eksik := beklenen - {d["id"] for d in temiz}:
        print(f"⚠️ cevapta olmayan {len(eksik)} şablon: {sorted(eksik)}")
    if sorun:
        print(f"⚠️ geçersiz {len(sorun)} öğe: {sorun[:3]}")


if __name__ == "__main__":
    arg = sys.argv[1:]
    if "--ilk" in arg:
        i = arg.index("--ilk")
        ILK_YENI = int(arg[i + 1])
        del arg[i:i + 2]
        ek = f"_{ILK_YENI}"   # önceki turun dosyaları korunur: paket_15.md, cevap_15.json, kararlar_15.jsonl
        PAKET, CEVAP, KARAR = DIZIN / f"paket{ek}.md", DIZIN / f"cevap{ek}.json", DIZIN / f"kararlar{ek}.jsonl"
    {"disari": disari, "iceri": iceri}[arg[0] if arg else "disari"]()
