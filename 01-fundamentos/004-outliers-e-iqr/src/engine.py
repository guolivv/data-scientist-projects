"""Motor do projeto 004 — Outliers e IQR."""

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
    col = "ticket" if "ticket" in frame.columns else frame.select_dtypes("number").columns[0]
    series = pd.to_numeric(frame[col], errors="coerce").dropna()
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    low, high = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    flagged = (series < low) | (series > high)
    winsor = series.clip(low, high)
    payload = {
        "coluna": str(col),
        "q1": float(q1),
        "q3": float(q3),
        "iqr": float(iqr),
        "n_outliers": int(flagged.sum()),
        "media_original": float(series.mean()),
        "media_winsor": float(winsor.mean()),
        "limites": [float(low), float(high)],
    }
    return dump_json(destination, payload)
