"""KALKAN · Adım 1 · ağırlık teşhisi (taban ↔ aday)               v1 · 2026-11-18

1 iterasyonluk LoRA'dan sonra aday model tabana NEREDEYSE EŞİT olmalı. Büyük farklar
dönüşüm hatası demektir. Raporlananlar:
  • isim eşleşmesi (eksik/fazla tensör; vision tensörleri ayrı sayılır)
  • şekil farkı ve bunun yalnızca eksen yerleşimi (ör. conv1d) olup olmadığı
  • dtype değişimi
  • norm ağırlıklarında ~+1 kayma (Qwen3.5 (1+w) RMSNorm; MLX sanitize ofset ekleyebilir)
  • en çok değişen tensörler

Kullanım: python inspect_weights.py <taban_klasör> <aday_klasör> [--json çıktı.json]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from safetensors import safe_open

PREFIXES = ("model.language_model.", "language_model.model.", "language_model.", "model.")
VISION = ("visual.", "vision_tower.", "vision_model.", "merger.", "multi_modal_projector.")


def canon(key: str) -> str:
    for p in PREFIXES:
        if key.startswith(p):
            return key[len(p):]
    return key


def index(d: Path) -> dict[str, tuple[Path, str]]:
    out = {}
    for sf in sorted(d.glob("*.safetensors")):
        with safe_open(str(sf), "pt") as f:
            for k in f.keys():
                out[canon(k)] = (sf, k)
    return out


def get(entry):
    sf, k = entry
    with safe_open(str(sf), "pt") as f:
        return f.get_tensor(k)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("base", type=Path)
    ap.add_argument("cand", type=Path)
    ap.add_argument("--json", type=Path)
    a = ap.parse_args()

    B, C = index(a.base), index(a.cand)
    is_vis = lambda k: k.startswith(VISION)  # noqa: E731
    missing = sorted(k for k in B if k not in C and not is_vis(k))
    extra = sorted(k for k in C if k not in B)
    vis_dropped = sum(1 for k in B if k not in C and is_vis(k))

    shape_diff, layout_only, dtype_diff, norm_shift, diffs = [], [], [], [], []
    for k in sorted(set(B) & set(C)):
        tb, tc = get(B[k]), get(C[k])
        if tb.dtype != tc.dtype:
            dtype_diff.append((k, str(tb.dtype), str(tc.dtype)))
        if tb.shape != tc.shape:
            (layout_only if sorted(tb.shape) == sorted(tc.shape) else shape_diff).append(
                (k, list(tb.shape), list(tc.shape)))
            continue
        d = (tc.float() - tb.float())
        mx = d.abs().max().item()
        diffs.append((k, mx, d.mean().item()))
        if k.endswith("norm.weight") and abs(d.mean().item() - 1.0) < 0.05:
            norm_shift.append(k)

    diffs.sort(key=lambda x: -x[1])
    changed = [x for x in diffs if x[1] > 0]
    rep = {
        "taban_tensor": len(B), "aday_tensor": len(C), "vision_dusen": vis_dropped,
        "eksik": missing[:20], "eksik_sayi": len(missing), "fazla": extra[:20], "fazla_sayi": len(extra),
        "sekil_farki": shape_diff[:20], "yerlesim_farki": layout_only[:20], "dtype_farki": dtype_diff[:10],
        "norm_plus1_kayma": norm_shift[:20], "norm_plus1_sayi": len(norm_shift),
        "degisen_tensor": len(changed), "en_cok_degisen": [(k, round(m, 6)) for k, m, _ in changed[:10]],
    }
    print(json.dumps(rep, ensure_ascii=False, indent=1))

    print("\nKARAR:")
    problems = []
    if rep["eksik_sayi"] or rep["fazla_sayi"]:
        problems.append("isim/tensör seti farklı → llama.cpp eşlemesi kırılabilir")
    if shape_diff or layout_only:
        problems.append("şekil/yerleşim farkı (ör. conv1d ekseni) → GGUF'ta sessiz bozulma riski")
    if norm_shift:
        problems.append(f"{len(norm_shift)} norm tensöründe +1 kayma → çift ofset = anlamsız çıktı riski")
    big = [k for k, m, _ in changed if m > 0.5]
    if big:
        problems.append(f"{len(big)} tensör 0.5'ten fazla değişmiş (1 iterasyon için beklenmez)")
    if not problems:
        print("  ✅ Aday, taban ile uyumlu; yalnızca LoRA hedefleri küçük oranda değişmiş.")
    for p in problems:
        print("  ❌", p)
    if a.json:
        rep["sorunlar"] = problems
        a.json.write_text(json.dumps(rep, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
