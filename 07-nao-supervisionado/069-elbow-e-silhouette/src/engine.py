"""Motor do projeto 069 — Elbow e silhouette."""

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
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

def run(source: Path, destination: Path) -> dict[str, Any]:
    x = StandardScaler().fit_transform(pd.read_csv(source))
    rows = []
    for k in range(2, 8):
        model = KMeans(n_clusters=k, n_init=10, random_state=42).fit(x)
        rows.append({"k": k, "inercia": float(model.inertia_), "silhouette": float(silhouette_score(x, model.labels_))})
    melhor = max(rows, key=lambda r: r["silhouette"])
    payload = {"curva": rows, "k_recomendado": melhor["k"]}
    return dump_json(destination, payload)
