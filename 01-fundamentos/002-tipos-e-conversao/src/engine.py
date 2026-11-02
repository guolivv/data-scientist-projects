"""Motor do projeto 002 — Tipos e conversão de colunas."""

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
    falhas: dict[str, int] = {}
    if "data" in frame.columns:
        parsed = pd.to_datetime(frame["data"], errors="coerce")
        falhas["data"] = int(parsed.isna().sum() - frame["data"].isna().sum())
        frame["data"] = parsed
    for col in ("quantidade", "receita", "preco"):
        if col not in frame.columns:
            continue
        numeric = pd.to_numeric(frame[col].astype(str).str.replace(",", ".", regex=False), errors="coerce")
        falhas[col] = int(numeric.isna().sum() - frame[col].isna().sum())
        frame[col] = numeric
    clean = destination.with_suffix(".csv")
    clean.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(clean, index=False)
    payload = {"linhas": int(len(frame)), "falhas_coercao": falhas, "arquivo_limpo": str(clean)}
    return dump_json(destination, payload)
