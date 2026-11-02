"""Motor do projeto 037 — Teste t de duas amostras."""

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
    a = frame.loc[frame["canal"] == "pago", "ticket"].dropna()
    b = frame.loc[frame["canal"] == "organico", "ticket"].dropna()
    ma, mb = float(a.mean()), float(b.mean())
    va, vb = float(a.var(ddof=1)), float(b.var(ddof=1))
    se = math.sqrt(va / len(a) + vb / len(b))
    t = (ma - mb) / se if se else 0.0
    df = len(a) + len(b) - 2
    p = 2 * (1 - 0.5 * (1 + math.erf(abs(t) / math.sqrt(2))))
    payload = {"n_pago": int(len(a)), "n_organico": int(len(b)), "media_pago": ma, "media_organico": mb, "t": t, "p_valor": float(p), "df": df}
    return dump_json(destination, payload)
