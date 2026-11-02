"""Motor do projeto 094 — Retreino versus freeze."""

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

from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source, parse_dates=["data"]).sort_values("data")
    y = frame["y"].to_numpy()
    t = np.arange(len(y)).reshape(-1, 1)
    cut = int(len(y) * 0.5)
    frozen = LinearRegression().fit(t[:cut], y[:cut])
    erros_freeze, erros_retrain = [], []
    for end in range(cut, len(y) - 7, 7):
        future_t, future_y = t[end : end + 7], y[end : end + 7]
        erros_freeze.append(mean_absolute_error(future_y, frozen.predict(future_t)))
        model = LinearRegression().fit(t[:end], y[:end])
        erros_retrain.append(mean_absolute_error(future_y, model.predict(future_t)))
    payload = {"mae_freeze": float(np.mean(erros_freeze)), "mae_retrain": float(np.mean(erros_retrain))}
    payload["recomendacao"] = "retreinar" if payload["mae_retrain"] < payload["mae_freeze"] else "congelar"
    return dump_json(destination, payload)
