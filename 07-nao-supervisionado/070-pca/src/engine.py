"""Motor do projeto 070 — PCA."""

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

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def run(source: Path, destination: Path) -> dict[str, Any]:
    x = StandardScaler().fit_transform(pd.read_csv(source))
    pca = PCA(n_components=2, random_state=42).fit(x)
    payload = {
        "variancia_explicada": pca.explained_variance_ratio_.tolist(),
        "variancia_acumulada": float(pca.explained_variance_ratio_.sum()),
        "n_componentes": 2,
    }
    return dump_json(destination, payload)
