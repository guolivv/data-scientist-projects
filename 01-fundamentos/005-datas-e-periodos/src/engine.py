"""Motor do projeto 005 — Datas e períodos."""

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
    col = "data" if "data" in frame.columns else "pedido_em"
    frame[col] = pd.to_datetime(frame[col], errors="coerce")
    frame["ano"] = frame[col].dt.year
    frame["mes"] = frame[col].dt.month
    frame["dia_semana"] = frame[col].dt.dayofweek
    valor = "receita" if "receita" in frame.columns else frame.select_dtypes("number").columns[0]
    mensal = frame.dropna(subset=[col]).groupby(["ano", "mes"], as_index=False)[valor].sum()
    csv_path = destination.with_name("serie_mensal.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    mensal.to_csv(csv_path, index=False)
    payload = {
        "linhas": int(len(frame)),
        "n_meses": int(len(mensal)),
        "min": str(frame[col].min()),
        "max": str(frame[col].max()),
        "arquivo_serie": str(csv_path),
    }
    return dump_json(destination, payload)
