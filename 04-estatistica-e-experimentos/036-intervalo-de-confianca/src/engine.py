"""Motor do projeto 036 — Intervalo de confiança."""

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
    p = float(frame["converteu"].mean())
    n = int(len(frame))
    se_p = math.sqrt(p * (1 - p) / max(n, 1))
    media = float(frame["ticket"].mean())
    se_m = float(frame["ticket"].std(ddof=1) / math.sqrt(n))
    z = 1.96
    payload = {
        "n": n,
        "conversao": p,
        "ic_conversao": [max(0, p - z * se_p), min(1, p + z * se_p)],
        "ticket": media,
        "ic_ticket": [media - z * se_m, media + z * se_m],
    }
    return dump_json(destination, payload)
