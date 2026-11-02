"""Motor do projeto 041 — Poder e tamanho amostral."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

def dump_json(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    p = float(frame["converteu"].mean())
    mde = 0.05
    alpha, power = 0.05, 0.8
    z_a, z_b = 1.96, 0.84
    n = 2 * p * (1 - p) * ((z_a + z_b) ** 2) / (mde ** 2)
    payload = {"baseline": p, "mde": mde, "alpha": alpha, "poder": power, "n_por_variante": int(math.ceil(n)), "n_observado": int(len(frame) // 2)}
    return dump_json(destination, payload)
