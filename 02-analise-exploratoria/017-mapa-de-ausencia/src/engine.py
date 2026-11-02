"""Motor do projeto 017 — Mapa de ausência."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def dump_json(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    por_coluna = {c: round(float(frame[c].isna().mean()), 4) for c in frame.columns}
    por_grupo = {}
    if "uf" in frame.columns and "renda" in frame.columns:
        por_grupo = frame.groupby("uf")["renda"].apply(lambda s: round(float(s.isna().mean()), 4)).to_dict()
    payload = {"por_coluna": por_coluna, "missing_renda_por_uf": por_grupo, "linhas": int(len(frame))}
    return dump_json(destination, payload)
