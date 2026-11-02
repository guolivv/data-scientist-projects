"""Motor do projeto 058 — Métricas de regressão."""

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
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["y"]
    x = frame.drop(columns=["y"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)
    pred = LinearRegression().fit(x_train, y_train).predict(x_test)
    mae = float(mean_absolute_error(y_test, pred))
    rmse = float(mean_squared_error(y_test, pred) ** 0.5)
    mape = float(np.mean(np.abs((y_test - pred) / np.clip(np.abs(y_test), 1e-6, None))))
    payload = {"rmse": rmse, "mae": mae, "mape": mape, "r2": float(r2_score(y_test, pred)), "unidade": "reais"}
    return dump_json(destination, payload)
