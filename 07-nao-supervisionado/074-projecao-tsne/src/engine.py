"""Motor do projeto 074 — Projeção t-SNE."""

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

from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler

def run(source: Path, destination: Path) -> dict[str, Any]:
    x = StandardScaler().fit_transform(pd.read_csv(source))
    coords = TSNE(n_components=2, perplexity=15, random_state=42, init="pca", learning_rate="auto").fit_transform(x)
    payload = {"n": int(len(coords)), "x_min": float(coords[:, 0].min()), "x_max": float(coords[:, 0].max()), "y_min": float(coords[:, 1].min()), "y_max": float(coords[:, 1].max())}
    csv_path = destination.with_name("tsne.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(coords, columns=["x", "y"]).to_csv(csv_path, index=False)
    payload["arquivo"] = str(csv_path)
    return dump_json(destination, payload)
