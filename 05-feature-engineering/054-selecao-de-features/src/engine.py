"""Motor do projeto 054 — Seleção de features."""

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
from sklearn.model_selection import train_test_split

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)
    model = RandomForestClassifier(n_estimators=80, random_state=42)
    model.fit(x_train, y_train)
    imp = pd.Series(model.feature_importances_, index=x.columns).sort_values(ascending=False)
    corr = x_train.join(y_train).corr()["alvo"].drop("alvo").abs().sort_values(ascending=False)
    payload = {
        "importancia": imp.round(4).to_dict(),
        "corr_alvo": corr.round(4).to_dict(),
        "top": list(imp.head(5).index),
        "acuracia": float(model.score(x_test, y_test)),
    }
    return dump_json(destination, payload)
