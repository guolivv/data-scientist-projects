"""Motor do projeto 068 — K-means."""

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

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    x = StandardScaler().fit_transform(frame)
    model = KMeans(n_clusters=3, n_init=10, random_state=42).fit(x)
    payload = {
        "k": 3,
        "inercia": float(model.inertia_),
        "tamanhos": pd.Series(model.labels_).value_counts().sort_index().to_dict(),
        "centroides": model.cluster_centers_.tolist(),
    }
    return dump_json(destination, payload)
