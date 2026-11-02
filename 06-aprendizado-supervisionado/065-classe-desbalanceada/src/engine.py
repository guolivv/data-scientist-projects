"""Motor do projeto 065 — Classe desbalanceada."""

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

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import recall_score, precision_score
from sklearn.model_selection import train_test_split

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["fraude"]
    x = frame.drop(columns=["fraude"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)
    plain = LogisticRegression(max_iter=300).fit(x_train, y_train)
    weighted = LogisticRegression(max_iter=300, class_weight="balanced").fit(x_train, y_train)
    def pack(model):
        pred = model.predict(x_test)
        return {"precision": float(precision_score(y_test, pred, zero_division=0)), "recall": float(recall_score(y_test, pred, zero_division=0)), "acuracia": float(model.score(x_test, y_test))}
    payload = {"prevalencia": float(y.mean()), "sem_peso": pack(plain), "com_peso": pack(weighted)}
    return dump_json(destination, payload)
