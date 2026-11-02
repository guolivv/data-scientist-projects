"""Motor do projeto 061 — Árvore de decisão."""

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

from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.model_selection import train_test_split

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)
    model = DecisionTreeClassifier(max_depth=3, random_state=42).fit(x_train, y_train)
    payload = {
        "acuracia": float(model.score(x_test, y_test)),
        "importancias": dict(zip(x.columns, model.feature_importances_.tolist())),
        "regras": export_text(model, feature_names=list(x.columns)),
        "profundidade": int(model.get_depth()),
    }
    return dump_json(destination, payload)
