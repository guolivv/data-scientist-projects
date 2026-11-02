"""Motor do projeto 098 — Recomendação simples ponta a ponta."""

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

def run(source: Path, destination: Path) -> dict[str, Any]:
    inter = pd.read_csv(source)
    mat = pd.crosstab(inter["usuario_id"], inter["item_id"])
    items = mat.columns.to_numpy()
    x = mat.to_numpy(dtype=float)
    norms = np.linalg.norm(x, axis=0, keepdims=True)
    norms[norms == 0] = 1
    sim = (x.T @ x) / (norms.T @ norms)
    np.fill_diagonal(sim, 0)
    topn = {}
    for i, item in enumerate(items):
        idx = sim[i].argsort()[::-1][:3]
        topn[str(item)] = [str(items[j]) for j in idx]
    cobertos = set(inter["usuario_id"])
    payload = {"n_usuarios": int(mat.shape[0]), "n_itens": int(mat.shape[1]), "topn": topn, "cobertura_usuarios": int(len(cobertos))}
    return dump_json(destination, payload)
