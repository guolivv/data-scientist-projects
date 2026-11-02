"""Motor do projeto 081 — Mudança de regime."""

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
    y = pd.read_csv(source, parse_dates=["data"]).sort_values("data")["y"].to_numpy(dtype=float)
    best_i, best_stat = None, -1.0
    for i in range(10, len(y) - 10):
        a, b = y[:i], y[i:]
        se = math.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
        stat = abs(a.mean() - b.mean()) / se if se else 0
        if stat > best_stat:
            best_stat, best_i = stat, i
    payload = {"indice_quebra": int(best_i), "estatistica": float(best_stat), "media_antes": float(y[:best_i].mean()), "media_depois": float(y[best_i:].mean())}
    return dump_json(destination, payload)
