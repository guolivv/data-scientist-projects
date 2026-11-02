"""Motor do projeto 035 — Estatística descritiva robusta."""

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
    series = pd.to_numeric(pd.read_csv(source)["ticket"], errors="coerce").dropna()
    med = float(series.median())
    mad = float(np.median(np.abs(series - med)))
    payload = {
        "media": float(series.mean()),
        "mediana": med,
        "iqr": float(series.quantile(0.75) - series.quantile(0.25)),
        "mad": mad,
        "recomendacao": "mediana" if abs(series.mean() - med) > series.std(ddof=1) * 0.25 else "media",
    }
    return dump_json(destination, payload)
