"""Motor do projeto 063 — Gradient boosting."""

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

from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import train_test_split

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)
    rf = RandomForestClassifier(n_estimators=80, random_state=42).fit(x_train, y_train)
    gb = GradientBoostingClassifier(n_estimators=60, max_depth=2, random_state=42).fit(x_train, y_train)
    payload = {
        "acuracia_rf": float(rf.score(x_test, y_test)),
        "acuracia_gb": float(gb.score(x_test, y_test)),
        "n_estimators_gb": 60,
    }
    return dump_json(destination, payload)
