"""Motor do projeto 100 — Laboratório local de ciência de dados."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def dump_json(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import hashlib, pickle

def psi(expected, actual, bins=8):
    edges = np.unique(np.quantile(expected, np.linspace(0, 1, bins + 1)))
    if len(edges) < 3:
        return 0.0
    e = np.clip(np.histogram(expected, bins=edges)[0] / len(expected), 1e-6, None)
    a = np.clip(np.histogram(actual, bins=edges)[0] / len(actual), 1e-6, None)
    return float(np.sum((a - e) * np.log(a / e)))

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)
    pipe = Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression(max_iter=300))])
    pipe.fit(x_train, y_train)
    auc = float(roc_auc_score(y_test, pipe.predict_proba(x_test)[:, 1]))
    drift = {c: psi(x_train[c].to_numpy(), x_test[c].to_numpy()) for c in x.columns}
    blob = pickle.dumps(pipe)
    art = destination.with_name("lab_model.pkl")
    art.parent.mkdir(parents=True, exist_ok=True)
    art.write_bytes(blob)
    card = destination.with_name("model_card.md")
    card.write_text(f"# Laboratório local\n\nAUC {auc:.3f}. Seed 42. Dado sintético.\n", encoding="utf-8")
    payload = {
        "auc": auc,
        "drift": drift,
        "sha256": hashlib.sha256(blob).hexdigest(),
        "artefato": str(art),
        "model_card": str(card),
        "linhas": int(len(frame)),
        "nulos": {c: int(frame[c].isna().sum()) for c in frame.columns},
    }
    return dump_json(destination, payload)
