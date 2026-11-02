"""Motor do projeto 093 — Threshold por custo de negócio."""

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

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)
    proba = LogisticRegression(max_iter=300).fit(x_train, y_train).predict_proba(x_test)[:, 1]
    custo_fp, custo_fn = 8, 40
    melhor = None
    for thr in np.linspace(0.1, 0.9, 17):
        pred = (proba >= thr).astype(int)
        fp = int(((pred == 1) & (y_test == 0)).sum())
        fn = int(((pred == 0) & (y_test == 1)).sum())
        custo = fp * custo_fp + fn * custo_fn
        cand = {"threshold": round(float(thr), 2), "custo": custo, "fp": fp, "fn": fn}
        if melhor is None or cand["custo"] < melhor["custo"]:
            melhor = cand
    payload = {"melhor": melhor, "custo_fp": custo_fp, "custo_fn": custo_fn}
    return dump_json(destination, payload)
