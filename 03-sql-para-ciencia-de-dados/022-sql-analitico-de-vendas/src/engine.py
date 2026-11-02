"""Motor do projeto 022 — SQL analítico de vendas."""

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
        frame.to_sql("vendas", conn, index=False, if_exists="replace")
        ranking = pd.read_sql("""
            SELECT categoria, ROUND(SUM(receita),2) AS receita,
                   ROUND(AVG(receita),2) AS ticket,
                   RANK() OVER (ORDER BY SUM(receita) DESC) AS rank
            FROM vendas GROUP BY categoria
        """, conn)
        mix = pd.read_sql("""
            SELECT canal, ROUND(100.0 * SUM(receita) / (SELECT SUM(receita) FROM vendas), 2) AS pct
            FROM vendas GROUP BY canal
        """, conn)
    payload = {"ranking": ranking.to_dict(orient="records"), "mix_canal": mix.to_dict(orient="records")}
    return dump_json(destination, payload)
