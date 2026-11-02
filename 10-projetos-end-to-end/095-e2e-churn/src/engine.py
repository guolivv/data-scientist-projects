"""Motor do projeto 095 — Churn de ponta a ponta."""

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
from sklearn.metrics import roc_auc_score, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["churn"]
    x = frame.drop(columns=["churn"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)
    pipe = Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression(max_iter=300))])
    pipe.fit(x_train, y_train)
    proba = pipe.predict_proba(x_test)[:, 1]
    pred = (proba >= 0.5).astype(int)
    md = destination.with_name("model_card.md")
    md.parent.mkdir(parents=True, exist_ok=True)
    auc = float(roc_auc_score(y_test, proba))
    md.write_text(f"# Churn\n\nROC-AUC {auc:.3f}. Dado sintético. Não usar em produção.\n", encoding="utf-8")
    payload = {"auc": auc, "f1": float(f1_score(y_test, pred)), "n": int(len(frame)), "model_card": str(md)}
    return dump_json(destination, payload)
