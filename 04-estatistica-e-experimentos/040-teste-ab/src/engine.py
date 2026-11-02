"""Motor do projeto 040 — Teste A/B clássico."""

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
    a = frame.loc[frame["variante"] == "A", "converteu"]
    b = frame.loc[frame["variante"] == "B", "converteu"]
    pa, pb = float(a.mean()), float(b.mean())
    na, nb = int(len(a)), int(len(b))
    p = (a.sum() + b.sum()) / (na + nb)
    se = math.sqrt(p * (1 - p) * (1 / na + 1 / nb))
    z = (pb - pa) / se if se else 0.0
    pval = 2 * (1 - 0.5 * (1 + math.erf(abs(z) / math.sqrt(2))))
    payload = {
        "conversao_a": pa, "conversao_b": pb, "n_a": na, "n_b": nb,
        "uplift_abs": pb - pa, "uplift_rel": (pb - pa) / pa if pa else None,
        "z": z, "p_valor": float(pval), "vencedor": "B" if pb > pa and pval < 0.05 else "inconclusivo",
    }
    return dump_json(destination, payload)
