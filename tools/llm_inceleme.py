"""KALKAN · Adım 3 · golden inceleme için LLM ön-elemesi              v1 · 2026-11-20

Amaç: 150 örneği farklı bir model ailesine (ör. Gemini) incelettirmek; insan yalnızca işaretlenenlere
ve rastgele bir "doğru" örneklemine bakar. Veri tamamen sentetiktir (gerçek kişisel veri yok).
⚠️ data/external/ altındaki dosyaları (özellikle UCI: gerçek e-postalar) ASLA bu yolla dışarı gönderme.

1) python tools/llm_inceleme.py disari        → data/golden/llm_paketi.md (yönerge + 150 örnek)
   Dosyayı Gemini'ye yükle (ya da içeriğini yapıştır). Cevabı data/golden/llm_cevap.json olarak kaydet.
2) python tools/llm_inceleme.py iceri         → data/golden/llm_kararlari.jsonl + özet
3) python tools/incele.py --teyit             → yalnızca işaretlenenler + 20 rastgele "doğru"
4) python tools/incele.py --birlestir         → golden.jsonl (öncelik: insan > LLM)
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK))
from kalkan.schema import Tur  # noqa: E402
from kalkan.taxonomy import yukle  # noqa: E402
from tools.incele import secim  # noqa: E402

PAKET = KOK / "data/golden/llm_paketi.md"
CEVAP = KOK / "data/golden/llm_cevap.json"
KARAR = KOK / "data/golden/llm_kararlari.jsonl"

YONERGE = """# Görev: Türkçe dolandırıcılık SMS veri setinin etiket denetimi

Sen bağımsız bir veri denetçisisin. Aşağıdaki {n} SENTETİK SMS mesajı bir başka model tarafından şablonlardan
üretildi ve etiketlendi. Görevin etiket hatalarını bulmak. Kurum adları ve numaralar uydurmadır.

## Her örnek için sırayla sor; "hayır" dediğin İLK soruda karar ver
1. Böyle bir SMS gerçek hayatta gelebilir mi? Anlamca çelişkili, saçma ya da okunamaz ise → "cikar"
2. Tür AÇIKÇA yanlış mı? → "tur" (+ yeni_tur)
3. Bir kanıt alıntısı yanındaki sinyalle AÇIKÇA uyuşmuyor mu, ya da mesajın ANA dolandırıcılık hamlesi
   kanıtlarda hiç yok mu? → "kanit"
4. Hiçbiri değilse → "dogru"

## Önemli kurallar
- Emin değilsen "dogru". İki tür de savunulabiliyorsa "dogru". Sadece AÇIK hataları işaretle.
- BİLİNÇLİ gürültü, hata DEĞİLDİR: Türkçe karaktersiz yazım, yazım hataları, çift boşluk, BÜYÜK HARF, emoji,
  uydurma marka adları, [TEL] [IBAN] [OTP] [KART] maske etiketleri.
- En fazla 3 kanıt seçilebilir; küçük ayrıntıların eksikliği hata değildir.
- reklam_spam ve mesru_islem için kanıt listesinin BOŞ olması doğrudur (kanıtlar yalnızca dolandırıcılık işaretleri içindir).
- Model risk seviyesi üretmez; risk değerlendirme.

## Türler
{turler}

## Sinyaller
{sinyaller}

## Çıktı biçimi (YALNIZCA geçerli bir JSON dizisi, başka metin yok; her örnek için tam bir öğe)
[{{"id": "tes-00134", "karar": "dogru"}},
 {{"id": "tes-00166", "karar": "kanit", "not": "kısa gerekçe"}},
 {{"id": "tes-00074", "karar": "tur", "yeni_tur": "mesru_islem", "not": "kısa gerekçe"}},
 {{"id": "tes-00012", "karar": "cikar", "not": "kısa gerekçe"}}]
"karar" ∈ dogru | tur | kanit | cikar. "dogru" dışındaki her kararda "not" zorunlu.

## Örnekler
"""


def disari() -> None:
    tax = yukle()
    turler = "\n".join(f"- {t['id']}: {t['tanim']} AYIRT EDİCİ: {t['ayirt_edici']}" for t in tax["turler"])
    sinyaller = "\n".join(f"- {s['id']}: {s['tanim']}" for s in tax["sinyaller"])
    sec = secim()
    parca = [YONERGE.format(n=len(sec), turler=turler, sinyaller=sinyaller)]
    for r in sec:
        k = "\n".join(f"  - {x['sinyal']}: \"{x['alinti']}\"" for x in r["hedef"]["kanitlar"]) or "  (yok)"
        parca.append(f"### {r['id']}\nMESAJ: {r['model_girdisi']}\nTÜR: {r['tur']}\nKANITLAR:\n{k}\n")
    PAKET.parent.mkdir(parents=True, exist_ok=True)
    PAKET.write_text("\n".join(parca), encoding="utf-8")
    print(f"{PAKET}  ({len(sec)} örnek, {PAKET.stat().st_size // 1024} KB)")


def iceri() -> None:
    ham = CEVAP.read_text(encoding="utf-8")
    ham = re.sub(r"^```(json)?|```\s*$", "", ham.strip(), flags=re.M).strip()   # kod bloğu sarmalayıcısı
    cevap = json.loads(ham)
    beklenen = {r["id"] for r in secim()}
    turler = {t.value for t in Tur}
    temiz, sorun = [], []
    for d in cevap:
        if d.get("id") not in beklenen or d.get("karar") not in ("dogru", "tur", "kanit", "cikar"):
            sorun.append(d)
            continue
        if d["karar"] == "tur" and d.get("yeni_tur") not in turler:
            sorun.append(d)
            continue
        temiz.append({**d, "kaynak": "llm"})
    eksik = beklenen - {d["id"] for d in temiz}
    with open(KARAR, "w", encoding="utf-8") as f:
        for d in temiz:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
    print(f"LLM kararı: {len(temiz)}/{len(beklenen)} · dağılım: {dict(Counter(d['karar'] for d in temiz))}")
    if eksik:
        print(f"⚠️ cevapta olmayan {len(eksik)} id (Gemini'den yalnızca bunları iste): {sorted(eksik)[:10]}…")
    if sorun:
        print(f"⚠️ geçersiz {len(sorun)} öğe atlandı: {sorun[:3]}")


if __name__ == "__main__":
    {"disari": disari, "iceri": iceri}[sys.argv[1] if len(sys.argv) > 1 else "disari"]()
