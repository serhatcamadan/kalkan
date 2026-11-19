"""KALKAN · Adım 1 · Yol B: MLX LoRA adaptörünü HF ağırlıklarına birleştir   v1 · 2026-11-18

Neden: `mlx_lm.fuse` çıktısı MLX'in iç düzenini (isimler, conv yerleşimi, norm ofseti)
taşıyabilir; llama.cpp ise ORİJİNAL HF düzenini bekler. Bu script orijinal HF klasörünü
olduğu gibi kopyalar ve yalnızca LoRA uygulanmış Linear ağırlıklarını değiştirir:

    W' = W + scale · (lora_a @ lora_b)ᵀ        (mlx LoRALinear: y = xWᵀ + scale·(x·A)·B)

Kullanım:
  python merge_mlx_adapter_hf.py --base .spike/base --adapter .spike/adapters --out .spike/merged_hf
"""
from __future__ import annotations

import argparse
import json
import shutil
from collections import defaultdict
from pathlib import Path

import torch
from safetensors import safe_open
from safetensors.torch import load_file, save_file

PREFIXES = ("model.language_model.", "language_model.model.", "language_model.", "model.")


def canon(key: str) -> str:
    """HF ve MLX isimlerini ortak 'metin modeli' son ekine indirger."""
    for p in PREFIXES:
        if key.startswith(p):
            return key[len(p):]
    return key


def load_adapter(adapter_dir: Path) -> tuple[dict[str, dict[str, torch.Tensor]], float, dict]:
    cfg = json.loads((adapter_dir / "adapter_config.json").read_text())
    if cfg.get("fine_tune_type", "lora") != "lora":
        raise SystemExit(f"Yalnızca LoRA destekleniyor, bulunan: {cfg.get('fine_tune_type')}")
    lp = cfg.get("lora_parameters", {})
    scale = float(lp.get("scale", 20.0))
    raw = load_file(str(adapter_dir / "adapters.safetensors"))
    mods: dict[str, dict[str, torch.Tensor]] = defaultdict(dict)
    for k, v in raw.items():
        mod, _, part = k.rpartition(".")
        if part not in ("lora_a", "lora_b"):
            raise SystemExit(f"Beklenmeyen adaptör anahtarı: {k}")
        mods[mod][part] = v
    return dict(mods), scale, cfg


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--adapter", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    mods, scale, cfg = load_adapter(a.adapter)
    print(f"adaptör: {len(mods)} modül, scale={scale}, rank={cfg.get('lora_parameters', {}).get('rank')}")

    # taban: anahtar → shard dosyası
    shards = sorted(a.base.glob("*.safetensors"))
    key_file: dict[str, Path] = {}
    for sf in shards:
        with safe_open(str(sf), "pt") as f:
            for k in f.keys():
                key_file[k] = sf
    by_canon: dict[str, list[str]] = defaultdict(list)
    for k in key_file:
        by_canon[canon(k)].append(k)

    # adaptör modülü → taban ağırlık anahtarı
    plan: dict[Path, dict[str, tuple[torch.Tensor, torch.Tensor]]] = defaultdict(dict)
    for mod, ab in mods.items():
        target = canon(mod) + ".weight"
        cands = by_canon.get(target, [])
        if len(cands) != 1:
            raise SystemExit(f"Eşleşme yok/çoklu: adaptör '{mod}' → '{target}' → {cands}")
        hf_key = cands[0]
        plan[key_file[hf_key]][hf_key] = (ab["lora_a"], ab["lora_b"])

    # çıktı klasörü: tabandaki her şey (config, tokenizer, processor, vision ağırlıkları dahil)
    if a.out.exists():
        shutil.rmtree(a.out)
    shutil.copytree(a.base, a.out, ignore=shutil.ignore_patterns("*.safetensors", ".cache"))

    stats = []
    for sf in shards:
        with safe_open(str(sf), "pt") as f:
            meta = f.metadata() or {}
        tensors = load_file(str(sf))
        for hf_key, (la, lb) in plan.get(sf, {}).items():
            w = tensors[hf_key]
            out_dim, in_dim = w.shape
            if la.shape[0] != in_dim or lb.shape[1] != out_dim:
                raise SystemExit(f"Şekil uyuşmazlığı {hf_key}: W{tuple(w.shape)} A{tuple(la.shape)} B{tuple(lb.shape)}")
            delta = scale * (la.float() @ lb.float()).T
            tensors[hf_key] = (w.float() + delta).to(w.dtype)
            stats.append((hf_key, delta.abs().mean().item(), delta.abs().max().item()))
        meta.setdefault("format", "pt")
        save_file(tensors, str(a.out / sf.name), metadata=meta)

    print(f"birleştirilen ağırlık: {len(stats)}")
    for k, mean, mx in stats[:8]:
        print(f"  {k}: |Δ| ort={mean:.2e} maks={mx:.2e}")
    if stats and max(s[2] for s in stats) == 0.0:
        print("UYARI: tüm Δ=0 → lora_b sıfır kalmış (eğitim adımı uygulanmamış olabilir).")
    (a.out / "kalkan_merge.json").write_text(json.dumps(
        {"adapter_config": cfg, "merged": [s[0] for s in stats]}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
