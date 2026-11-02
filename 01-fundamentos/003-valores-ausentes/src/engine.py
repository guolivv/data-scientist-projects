"""Motor do projeto 003 — Valores ausentes."""

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
    n = len(frame)
    relatorio = {}
    for col in frame.columns:
        nulos = int(frame[col].isna().sum())
        relatorio[str(col)] = {"nulos": nulos, "pct": round(100 * nulos / max(n, 1), 2)}
    numeric = frame.select_dtypes(include=["number"])
    imputed = frame.copy()
    for col in numeric.columns:
        imputed[col] = imputed[col].fillna(imputed[col].median())
    dropped = frame.dropna()
    payload = {
        "linhas": n,
        "por_coluna": relatorio,
        "linhas_apos_dropna": int(len(dropped)),
        "linhas_apos_mediana": int(len(imputed)),
        "impacto_dropna": int(n - len(dropped)),
    }
    return dump_json(destination, payload)
