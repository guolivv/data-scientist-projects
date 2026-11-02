"""Motor do projeto 078 — Baseline naive e sazonal."""

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
    split = int(len(y) * 0.7)
    test = y[split:]
    naive = np.repeat(y[split - 1], len(test))
    sazonal = np.array([y[split - 7 + (i % 7)] for i in range(len(test))])
    def mae(a, b):
        return float(np.mean(np.abs(a - b)))
    payload = {"mae_naive": mae(test, naive), "mae_sazonal": mae(test, sazonal), "n_teste": int(len(test))}
    return dump_json(destination, payload)
