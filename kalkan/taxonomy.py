"""KALKAN · taxonomy.py — data/taxonomy.yaml yükleyici              v1 · 2026-11-19"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

YOL = Path(__file__).resolve().parents[1] / "data" / "taxonomy.yaml"


@lru_cache(maxsize=1)
def yukle(yol: Path = YOL) -> dict:
    with open(yol, encoding="utf-8") as f:
        return yaml.safe_load(f)
