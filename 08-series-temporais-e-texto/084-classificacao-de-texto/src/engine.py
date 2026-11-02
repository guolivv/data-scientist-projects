"""Motor do projeto 084 — Classificação de texto."""

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

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC
from sklearn.metrics import f1_score

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    x_train, x_test, y_train, y_test = train_test_split(frame["texto"], frame["fila"], test_size=0.3, random_state=42, stratify=frame["fila"])
    pipe = Pipeline([("tfidf", TfidfVectorizer(max_features=120)), ("clf", LinearSVC())])
    pipe.fit(x_train, y_train)
    pred = pipe.predict(x_test)
    payload = {"macro_f1": float(f1_score(y_test, pred, average="macro")), "classes": sorted(frame["fila"].unique().tolist())}
    return dump_json(destination, payload)
