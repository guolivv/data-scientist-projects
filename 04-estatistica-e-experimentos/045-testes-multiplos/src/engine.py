"""Motor do projeto 045 — Testes múltiplos."""

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
    frame = pd.read_csv(source)
    pvals = frame["p_valor"].astype(float).to_numpy()
    m = len(pvals)
    bonf = np.minimum(pvals * m, 1)
    order = np.argsort(pvals)
    ranked = pvals[order]
    fdr = np.empty(m)
    prev = 1.0
    for i in range(m, 0, -1):
        val = ranked[i - 1] * m / i
        prev = min(prev, val)
        fdr[i - 1] = min(prev, 1)
    adj = np.empty(m)
    adj[order] = fdr
    payload = {
        "n_testes": m,
        "significativos_brutos": int((pvals < 0.05).sum()),
        "significativos_bonferroni": int((bonf < 0.05).sum()),
        "significativos_fdr": int((adj < 0.05).sum()),
    }
    return dump_json(destination, payload)
