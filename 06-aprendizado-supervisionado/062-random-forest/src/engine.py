"""Motor do projeto 062 — Random Forest."""

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
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42, stratify=y)
    tree = DecisionTreeClassifier(max_depth=6, random_state=42).fit(x_train, y_train)
    forest = RandomForestClassifier(n_estimators=120, random_state=42).fit(x_train, y_train)
    payload = {
        "acuracia_arvore": float(tree.score(x_test, y_test)),
        "acuracia_floresta": float(forest.score(x_test, y_test)),
        "ganho": float(forest.score(x_test, y_test) - tree.score(x_test, y_test)),
    }
    return dump_json(destination, payload)
