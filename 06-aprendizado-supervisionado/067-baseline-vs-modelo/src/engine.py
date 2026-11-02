"""Motor do projeto 067 — Baseline versus modelo."""

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

from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)
    dummy = DummyClassifier(strategy="most_frequent").fit(x_train, y_train)
    regra = (x_test.iloc[:, 0] > x_train.iloc[:, 0].median()).astype(int)
    model = LogisticRegression(max_iter=300).fit(x_train, y_train)
    payload = {
        "f1_dummy": float(f1_score(y_test, dummy.predict(x_test), zero_division=0)),
        "f1_regra": float(f1_score(y_test, regra, zero_division=0)),
        "f1_modelo": float(f1_score(y_test, model.predict(x_test), zero_division=0)),
    }
    return dump_json(destination, payload)
