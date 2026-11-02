"""Motor do projeto 089 — Importância por permutação."""

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

from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
from sklearn.model_selection import train_test_split

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)
    model = RandomForestClassifier(n_estimators=80, random_state=42).fit(x_train, y_train)
    perm = permutation_importance(model, x_test, y_test, n_repeats=8, random_state=42)
    payload = {
        "nativa": dict(zip(x.columns, model.feature_importances_.tolist())),
        "permutacao": dict(zip(x.columns, perm.importances_mean.tolist())),
    }
    return dump_json(destination, payload)
