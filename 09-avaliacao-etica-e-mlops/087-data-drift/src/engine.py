"""Motor do projeto 087 — Data drift."""

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

def psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    qs = np.linspace(0, 1, bins + 1)
    edges = np.unique(np.quantile(expected, qs))
    if len(edges) < 3:
        return 0.0
    e = np.clip(np.histogram(expected, bins=edges)[0] / len(expected), 1e-6, None)
    a = np.clip(np.histogram(actual, bins=edges)[0] / len(actual), 1e-6, None)
    return float(np.sum((a - e) * np.log(a / e)))

def run(source: Path, destination: Path) -> dict[str, Any]:
    treino = pd.read_csv(source)
    atual = pd.read_csv(source.with_name("atual.csv"))
    colunas = [c for c in treino.columns if c in atual.columns and np.issubdtype(treino[c].dtype, np.number)]
    rel = {c: psi(treino[c].dropna().to_numpy(), atual[c].dropna().to_numpy()) for c in colunas}
    payload = {"psi": rel, "alerta": [c for c, v in rel.items() if v > 0.2]}
    return dump_json(destination, payload)
