"""Motor do projeto 071 — Clustering hierárquico."""

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

from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler

def run(source: Path, destination: Path) -> dict[str, Any]:
    x = StandardScaler().fit_transform(pd.read_csv(source))
    model = AgglomerativeClustering(n_clusters=3, linkage="ward").fit(x)
    payload = {"k": 3, "tamanhos": pd.Series(model.labels_).value_counts().sort_index().to_dict(), "linkage": "ward"}
    return dump_json(destination, payload)
