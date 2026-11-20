"""KALKAN · Model 1: TF-IDF + Lojistik Regresyon                      v1 · 2026-11-20

Klasik metin sınıflandırma taban çizgisi. Girdi: maskeli metnin ASCII-katlanmış küçük harf hali.
Özellikler: karakter 2–5 gram (yazım hatası / Türkçe karaktersiz yazıma dayanıklı) + kelime 1–2 gram.
C (düzenleme gücü) yalnızca DOĞRULAMA setinde seçilir; golden hiçbir ayarda kullanılmaz.
Kanıt üretmez (H3: "tür bulur ama neden'ini söyleyemez") → kanıt metrikleri boş.
"""
from __future__ import annotations

import time

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline

from kalkan.normalize import Metin

from ..metrics import Tahmin, tur_metrikleri

C_IZGARA = [0.3, 1.0, 3.0, 10.0, 30.0]


def _metin(o: dict) -> str:
    return Metin(o["model_girdisi"]).ascii


def _boru(c: float) -> Pipeline:
    return Pipeline([
        ("ozellik", FeatureUnion([
            ("karakter", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2, sublinear_tf=True)),
            ("kelime", TfidfVectorizer(analyzer="word", ngram_range=(1, 2), min_df=2, sublinear_tf=True)),
        ])),
        ("sinif", LogisticRegression(C=c, max_iter=3000, class_weight="balanced")),
    ])


class TfidfModeli:
    ad = "tfidf"

    def __init__(self):
        self.boru: Pipeline | None = None

    def hazirla(self, egitim: list[dict], dogrulama: list[dict]) -> dict:
        X, y = [_metin(o) for o in egitim], [o["tur"] for o in egitim]
        Xd, yd = [_metin(o) for o in dogrulama], [o["tur"] for o in dogrulama]
        skor = {}
        for c in C_IZGARA:
            b = _boru(c).fit(X, y)
            skor[c] = tur_metrikleri(yd, list(b.predict(Xd)))["makro_f1"]
        en_iyi = max(skor, key=lambda c: (skor[c], -c))   # eşitlikte daha güçlü düzenleme (küçük C)
        self.boru = _boru(en_iyi).fit(X, y)
        return {"C_secimi_dogrulama_makro_f1": skor, "secilen_C": en_iyi}

    def tahmin(self, o: dict) -> Tahmin:
        t0 = time.perf_counter()
        tur = self.boru.predict([_metin(o)])[0]
        return Tahmin(tur=str(tur), kanitlar=[], sure_ms=(time.perf_counter() - t0) * 1000)
