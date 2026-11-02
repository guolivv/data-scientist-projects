"""Motor do projeto 043 — Mann-Whitney."""

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
    a = frame.loc[frame["plano"] == "plus", "gasto"].dropna().to_numpy()
    b = frame.loc[frame["plano"] == "basic", "gasto"].dropna().to_numpy()
    combined = np.concatenate([a, b])
    ranks = pd.Series(combined).rank().to_numpy()
    u = ranks[: len(a)].sum() - len(a) * (len(a) + 1) / 2
    mu = len(a) * len(b) / 2
    sigma = math.sqrt(len(a) * len(b) * (len(a) + len(b) + 1) / 12)
    z = (u - mu) / sigma if sigma else 0.0
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
    payload = {"u": float(u), "z": z, "p_valor": float(p), "media_plus": float(a.mean()), "media_basic": float(b.mean())}
    return dump_json(destination, payload)
