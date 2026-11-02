"""Motor do projeto 007 — Agrupamentos e KPIs."""

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
    grouped = frame.groupby(["categoria", "canal"], as_index=False).agg(
        pedidos=("pedido_id", "nunique") if "pedido_id" in frame.columns else ("receita", "size"),
        receita=("receita", "sum"),
        ticket=("receita", "mean"),
    )
    grouped["ticket"] = grouped["ticket"].round(2)
    grouped["receita"] = grouped["receita"].round(2)
    csv_path = destination.with_name("kpis.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    grouped.to_csv(csv_path, index=False)
    payload = {
        "n_grupos": int(len(grouped)),
        "receita_total": float(frame["receita"].sum()),
        "ticket_geral": round(float(frame["receita"].mean()), 2),
        "arquivo": str(csv_path),
    }
    return dump_json(destination, payload)
