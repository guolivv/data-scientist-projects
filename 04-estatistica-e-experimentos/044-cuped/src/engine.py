"""Motor do projeto 044 — CUPED e covariáveis."""

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
    y, x = frame["y"], frame["x_pre"]
    theta = float(np.cov(y, x, ddof=1)[0, 1] / np.var(x, ddof=1))
    y_adj = y - theta * (x - x.mean())
    var_before = float(y.var(ddof=1))
    var_after = float(y_adj.var(ddof=1))
    a = y_adj[frame["variante"] == "A"]
    b = y_adj[frame["variante"] == "B"]
    payload = {
        "theta": theta,
        "var_antes": var_before,
        "var_depois": var_after,
        "reducao": round(1 - var_after / var_before, 4),
        "media_a_ajustada": float(a.mean()),
        "media_b_ajustada": float(b.mean()),
    }
    return dump_json(destination, payload)
