"""Motor do projeto 030 — KPIs versionados em SQL."""

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
    with sqlite3.connect(":memory:") as conn:
        frame.to_sql("fatos", conn, index=False, if_exists="replace")
        kpis = pd.read_sql("""
            SELECT DATE(data) AS dia,
                   ROUND(SUM(receita),2) AS receita,
                   ROUND(SUM(receita - custo),2) AS margem,
                   ROUND(1.0 * SUM(receita - custo) / NULLIF(SUM(receita),0), 4) AS margem_pct
            FROM fatos GROUP BY DATE(data) ORDER BY 1
        """, conn)
    dicionario = {
        "receita": "soma de receita bruta do dia",
        "margem": "receita menos custo",
        "margem_pct": "margem / receita",
    }
    payload = {"kpis": kpis.to_dict(orient="records"), "dicionario": dicionario}
    return dump_json(destination, payload)
