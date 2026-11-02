"""Motor do projeto 080 — Backtest temporal."""

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
    cortes = [int(len(y) * p) for p in (0.5, 0.65, 0.8)]
    linhas = []
    for cut in cortes:
        hist, future = y[:cut], y[cut : cut + 7]
        pred = np.repeat(hist[-1], len(future))
        linhas.append({"corte": int(cut), "mae": float(np.mean(np.abs(future - pred)))})
    payload = {"cortes": linhas, "mae_medio": float(np.mean([r["mae"] for r in linhas]))}
    return dump_json(destination, payload)
