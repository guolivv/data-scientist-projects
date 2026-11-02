"""Motor do projeto 010 — Perfil estatístico de dataset."""

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
    numeric = frame.select_dtypes(include=["number"])
    perfil = {}
    for col in numeric.columns:
        series = numeric[col].dropna()
        perfil[str(col)] = {
            "n": int(series.size),
            "media": float(series.mean()) if len(series) else None,
            "mediana": float(series.median()) if len(series) else None,
            "desvio": float(series.std(ddof=1)) if len(series) > 1 else 0.0,
            "assimetria": float(series.skew()) if len(series) > 2 else 0.0,
            "nunique": int(series.nunique()),
            "nulos": int(frame[col].isna().sum()),
        }
    payload = {"linhas": int(len(frame)), "perfil": perfil, "categoricas": {c: int(frame[c].nunique()) for c in frame.select_dtypes(exclude=["number"]).columns}}
    return dump_json(destination, payload)
