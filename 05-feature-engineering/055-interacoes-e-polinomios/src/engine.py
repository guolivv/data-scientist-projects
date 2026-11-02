"""Motor do projeto 055 — Interações e polinômios."""

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
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["y"]
    x = frame[["preco", "categoria_code"]]
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)
    base = LinearRegression().fit(x_train, y_train)
    poly = PolynomialFeatures(degree=2, interaction_only=True, include_bias=False)
    xp_train, xp_test = poly.fit_transform(x_train), poly.transform(x_test)
    rich = LinearRegression().fit(xp_train, y_train)
    payload = {
        "r2_baseline": float(r2_score(y_test, base.predict(x_test))),
        "r2_interacao": float(r2_score(y_test, rich.predict(xp_test))),
        "features": list(poly.get_feature_names_out(x.columns)),
    }
    return dump_json(destination, payload)
