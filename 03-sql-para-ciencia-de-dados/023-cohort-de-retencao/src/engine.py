"""Motor do projeto 023 — Cohort de retenção."""

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
    frame = pd.read_csv(source, parse_dates=["data"])
    frame["mes"] = frame["data"].dt.to_period("M").astype(str)
    with sqlite3.connect(":memory:") as conn:
        frame.to_sql("pedidos", conn, index=False, if_exists="replace")
        cohort = pd.read_sql("""
            WITH primeira AS (
              SELECT cliente_id, MIN(mes) AS cohort FROM pedidos GROUP BY cliente_id
            )
            SELECT p.cohort, ped.mes, COUNT(DISTINCT ped.cliente_id) AS ativos
            FROM pedidos ped
            JOIN primeira p ON p.cliente_id = ped.cliente_id
            GROUP BY p.cohort, ped.mes
            ORDER BY p.cohort, ped.mes
        """, conn)
        tamanho = pd.read_sql("SELECT cohort, COUNT(*) AS n FROM (SELECT cliente_id, MIN(mes) AS cohort FROM pedidos GROUP BY cliente_id) t GROUP BY cohort", conn)
    payload = {"matriz": cohort.to_dict(orient="records"), "tamanhos": tamanho.to_dict(orient="records")}
    return dump_json(destination, payload)
