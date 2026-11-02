"""Motor do projeto 059 — Regressão logística."""

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
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, log_loss

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["churn"]
    x = frame.drop(columns=["churn"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)
    model = LogisticRegression(max_iter=300).fit(x_train, y_train)
    proba = model.predict_proba(x_test)[:, 1]
    payload = {
        "acuracia": float(accuracy_score(y_test, (proba >= 0.5).astype(int))),
        "log_loss": float(log_loss(y_test, proba)),
        "odds": dict(zip(x.columns, np.exp(model.coef_[0]).tolist())),
        "intercepto": float(model.intercept_[0]),
    }
    return dump_json(destination, payload)
