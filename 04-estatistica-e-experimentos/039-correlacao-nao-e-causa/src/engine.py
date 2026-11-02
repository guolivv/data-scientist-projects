"""Motor do projeto 039 — Correlação não é causa."""

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
    geral = float(frame[["x", "y"]].corr().iloc[0, 1])
    por_grupo = {str(name): float(g[["x", "y"]].corr().iloc[0, 1]) for name, g in frame.groupby("grupo")}
    payload = {
        "correlacao_agregada": geral,
        "por_grupo": por_grupo,
        "inversao": (geral > 0 and min(por_grupo.values()) < 0) or (geral < 0 and max(por_grupo.values()) > 0),
    }
    return dump_json(destination, payload)
