"""Motor do projeto 064 — Validação cruzada."""

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
from sklearn.model_selection import cross_val_score

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    scores = cross_val_score(LogisticRegression(max_iter=300), x, y, cv=5, scoring="accuracy")
    payload = {"folds": scores.tolist(), "media": float(scores.mean()), "desvio": float(scores.std(ddof=1)), "k": 5}
    return dump_json(destination, payload)
