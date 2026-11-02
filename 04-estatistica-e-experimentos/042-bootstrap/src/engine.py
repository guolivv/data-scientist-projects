"""Motor do projeto 042 — Bootstrap."""

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
    series = pd.to_numeric(pd.read_csv(source)["ticket"], errors="coerce").dropna().to_numpy()
    rng = np.random.default_rng(42)
    boots = np.array([np.median(rng.choice(series, size=len(series), replace=True)) for _ in range(400)])
    payload = {
        "mediana": float(np.median(series)),
        "ic_bootstrap": [float(np.quantile(boots, 0.025)), float(np.quantile(boots, 0.975))],
        "n_boot": 400,
    }
    return dump_json(destination, payload)
