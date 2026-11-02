"""Motor do projeto 097 — Credit scoring ponta a ponta."""

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
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import hashlib, pickle

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["inadimplente"]
    grupo = frame["grupo"]
    x = frame.drop(columns=["inadimplente", "grupo"])
    x_train, x_test, y_train, y_test, g_train, g_test = train_test_split(x, y, grupo, test_size=0.3, random_state=42, stratify=y)
    pipe = Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression(max_iter=300))])
    pipe.fit(x_train, y_train)
    proba = pipe.predict_proba(x_test)[:, 1]
    pred = (proba >= 0.5).astype(int)
    taxas = pd.Series(pred, index=g_test.index).groupby(g_test).mean().to_dict()
    vals = list(taxas.values())
    razao = min(vals) / max(vals) if max(vals) else None
    art = destination.with_name("score.pkl")
    art.parent.mkdir(parents=True, exist_ok=True)
    blob = pickle.dumps(pipe)
    art.write_bytes(blob)
    payload = {
        "auc": float(roc_auc_score(y_test, proba)),
        "taxas_grupo": {str(k): float(v) for k, v in taxas.items()},
        "razao_disparidade": razao,
        "sha256": hashlib.sha256(blob).hexdigest(),
        "artefato": str(art),
    }
    return dump_json(destination, payload)
