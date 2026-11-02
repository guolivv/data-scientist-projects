"""Motor do projeto 060 — Matriz de confusão e threshold."""

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
from sklearn.metrics import confusion_matrix, precision_score, recall_score

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)
    proba = LogisticRegression(max_iter=300).fit(x_train, y_train).predict_proba(x_test)[:, 1]
    linhas = []
    for thr in np.linspace(0.2, 0.8, 7):
        pred = (proba >= thr).astype(int)
        tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()
        custo = fp * 10 + fn * 50
        linhas.append({"threshold": round(float(thr), 2), "precision": float(precision_score(y_test, pred, zero_division=0)), "recall": float(recall_score(y_test, pred, zero_division=0)), "custo": int(custo), "fp": int(fp), "fn": int(fn)})
    melhor = min(linhas, key=lambda r: r["custo"])
    payload = {"varredura": linhas, "melhor": melhor}
    return dump_json(destination, payload)
