"""Motor do projeto 077 — Decomposição de série."""

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
    frame = pd.read_csv(source, parse_dates=["data"]).sort_values("data")
    y = frame["y"].to_numpy(dtype=float)
    period = 7
    seasonal = np.array([y[i::period].mean() for i in range(period)])
    seasonal = seasonal - seasonal.mean()
    seas = np.tile(seasonal, int(math.ceil(len(y) / period)))[: len(y)]
    kernel = np.ones(period) / period
    trend = np.convolve(y, kernel, mode="same")
    resid = y - trend - seas
    payload = {
        "n": int(len(y)),
        "periodo": period,
        "var_tendencia": float(np.var(trend)),
        "var_sazonal": float(np.var(seas)),
        "var_residuo": float(np.var(resid)),
    }
    return dump_json(destination, payload)
