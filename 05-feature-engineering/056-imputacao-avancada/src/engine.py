"""Motor do projeto 056 — Imputação avançada."""

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

from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    x_ind = x.copy()
    for col in x.columns:
        x_ind[f"{col}_missing"] = x[col].isna().astype(int)
    results = {}
    for name, xx in (("mediana", x), ("mediana_mais_indicador", x_ind)):
        x_train, x_test, y_train, y_test = train_test_split(xx, y, test_size=0.3, random_state=42)
        pipe = Pipeline([("imp", SimpleImputer(strategy="median")), ("clf", LogisticRegression(max_iter=200))])
        pipe.fit(x_train, y_train)
        results[name] = float(pipe.score(x_test, y_test))
    payload = {"acuracias": results, "taxa_nulos": {c: float(frame[c].isna().mean()) for c in frame.columns if c != "alvo"}}
    return dump_json(destination, payload)
