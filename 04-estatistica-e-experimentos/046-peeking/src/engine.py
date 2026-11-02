"""Motor do projeto 046 — Peeking e tamanho fixo."""

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
    rng = np.random.default_rng(0)
    n_sims, n = 200, int(len(frame))
    fp_peek = 0
    fp_fixo = 0
    for _ in range(n_sims):
        a = rng.binomial(1, 0.1, n)
        b = rng.binomial(1, 0.1, n)
        peeked = False
        for k in range(40, n + 1, 20):
            pa, pb = a[:k].mean(), b[:k].mean()
            p = (a[:k].sum() + b[:k].sum()) / (2 * k)
            se = math.sqrt(p * (1 - p) * (2 / k))
            z = abs(pb - pa) / se if se else 0
            pval = 2 * (1 - 0.5 * (1 + math.erf(z / math.sqrt(2))))
            if pval < 0.05:
                peeked = True
                break
        fp_peek += int(peeked)
        pa, pb = a.mean(), b.mean()
        p = (a.sum() + b.sum()) / (2 * n)
        se = math.sqrt(p * (1 - p) * (2 / n))
        z = abs(pb - pa) / se if se else 0
        pval = 2 * (1 - 0.5 * (1 + math.erf(z / math.sqrt(2))))
        fp_fixo += int(pval < 0.05)
    payload = {"falso_positivo_peeking": fp_peek / n_sims, "falso_positivo_n_fixo": fp_fixo / n_sims, "simulacoes": n_sims}
    return dump_json(destination, payload)
