"""Motor do projeto 057 — Regressão linear."""

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
from sklearn.metrics import mean_squared_error, r2_score

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["preco"]
    x = frame[["area", "quartos", "idade"]]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)
    model = LinearRegression().fit(x_train, y_train)
    pred = model.predict(x_test)
    payload = {
        "coeficientes": dict(zip(x.columns, model.coef_.tolist())),
        "intercepto": float(model.intercept_),
        "rmse": float(mean_squared_error(y_test, pred) ** 0.5),
        "r2": float(r2_score(y_test, pred)),
        "n_treino": int(len(x_train)),
        "n_teste": int(len(x_test)),
    }
    return dump_json(destination, payload)
