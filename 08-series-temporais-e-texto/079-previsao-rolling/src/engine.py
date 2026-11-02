"""Motor do projeto 079 — Previsão rolling."""

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
    janela = 7
    preds, reals = [], []
    for t in range(janela, len(y)):
        preds.append(float(y[t - janela : t].mean()))
        reals.append(float(y[t]))
    mae = float(np.mean(np.abs(np.array(reals) - np.array(preds))))
    payload = {"mae": mae, "janela": janela, "n_previsoes": len(preds)}
    return dump_json(destination, payload)
