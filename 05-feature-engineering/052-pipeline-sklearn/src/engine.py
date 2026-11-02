"""Motor do projeto 052 — Pipeline sklearn."""

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

from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.model_selection import train_test_split
import pickle

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    numeric = x.select_dtypes("number").columns.tolist()
    cats = x.select_dtypes(exclude="number").columns.tolist()
    pre = ColumnTransformer([
        ("num", StandardScaler(), numeric),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cats),
    ])
    pipe = Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=200))])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)
    pipe.fit(x_train, y_train)
    acc = float(pipe.score(x_test, y_test))
    art = destination.with_name("pipeline.pkl")
    art.parent.mkdir(parents=True, exist_ok=True)
    art.write_bytes(pickle.dumps(pipe))
    payload = {"acuracia_holdout": acc, "artefato": str(art), "passos": list(pipe.named_steps)}
    return dump_json(destination, payload)
