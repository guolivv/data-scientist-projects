"""Motor do projeto 031 — Features agregadas via SQL."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import sqlite3

def dump_json(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload

def run(source: Path, destination: Path) -> dict[str, Any]:
    eventos = pd.read_csv(source, parse_dates=["data"])
    pontos = eventos[["cliente_id"]].drop_duplicates().copy()
    pontos["cutoff"] = eventos["data"].max()
    feats = []
    for row in pontos.itertuples():
        hist = eventos[(eventos["cliente_id"] == row.cliente_id) & (eventos["data"] < row.cutoff)]
        janela = hist[hist["data"] >= row.cutoff - pd.Timedelta(days=30)]
        feats.append({
            "cliente_id": row.cliente_id,
            "pedidos_30d": int(len(janela)),
            "receita_30d": float(janela["receita"].sum()) if len(janela) else 0.0,
            "recencia": None if hist.empty else int((row.cutoff - hist["data"].max()).days),
        })
    payload = {"features": feats, "cutoff": str(pontos["cutoff"].iloc[0].date())}
    return dump_json(destination, payload)
