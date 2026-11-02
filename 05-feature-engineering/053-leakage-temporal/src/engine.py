"""Motor do projeto 053 — Leakage temporal."""

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
    eventos = pd.read_csv(source, parse_dates=["data"])
    pontos = eventos.groupby("cliente_id", as_index=False)["data"].max().rename(columns={"data": "cutoff"})
    leak, limpo = [], []
    for row in pontos.itertuples():
        hist_leak = eventos[(eventos["cliente_id"] == row.cliente_id) & (eventos["data"] <= row.cutoff)]
        hist_ok = eventos[(eventos["cliente_id"] == row.cliente_id) & (eventos["data"] < row.cutoff)]
        leak.append(float(hist_leak["receita"].sum()))
        limpo.append(float(hist_ok["receita"].sum()))
    payload = {
        "media_com_leakage": float(np.mean(leak)),
        "media_sem_leakage": float(np.mean(limpo)),
        "diferenca": float(np.mean(leak) - np.mean(limpo)),
        "regra": "janela exclusiva: data < cutoff",
    }
    return dump_json(destination, payload)
