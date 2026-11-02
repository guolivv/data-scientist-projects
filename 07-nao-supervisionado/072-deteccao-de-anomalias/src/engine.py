"""Motor do projeto 072 — Detecção de anomalias."""

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

from sklearn.ensemble import IsolationForest

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    model = IsolationForest(contamination=0.05, random_state=42).fit(frame)
    pred = model.predict(frame)
    scores = model.decision_function(frame)
    payload = {
        "n_anomalias": int((pred == -1).sum()),
        "taxa": float((pred == -1).mean()),
        "score_min": float(scores.min()),
        "score_max": float(scores.max()),
    }
    return dump_json(destination, payload)
