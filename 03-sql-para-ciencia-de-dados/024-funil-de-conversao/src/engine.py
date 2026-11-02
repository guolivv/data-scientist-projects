"""Motor do projeto 024 — Funil de conversão."""

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
    frame = pd.read_csv(source)
    ordem = ["visita", "cadastro", "checkout", "compra"]
    with sqlite3.connect(":memory:") as conn:
        frame.to_sql("eventos", conn, index=False, if_exists="replace")
        counts = pd.read_sql("SELECT etapa, COUNT(DISTINCT usuario_id) AS n FROM eventos GROUP BY etapa", conn)
    mapa = {row.etapa: int(row.n) for row in counts.itertuples()}
    funil = []
    prev = None
    for etapa in ordem:
        n = mapa.get(etapa, 0)
        taxa = None if prev in (None, 0) else round(n / prev, 4)
        funil.append({"etapa": etapa, "n": n, "taxa_vs_anterior": taxa})
        prev = n
    payload = {"funil": funil, "conversao_final": None if not funil[0]["n"] else round(funil[-1]["n"] / funil[0]["n"], 4)}
    return dump_json(destination, payload)
