"""Motor do projeto 026 — Funções de janela para DS."""

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
    with sqlite3.connect(":memory:") as conn:
        frame.to_sql("serie", conn, index=False, if_exists="replace")
        out = pd.read_sql("""
            SELECT data, receita,
                   LAG(receita, 1) OVER (ORDER BY data) AS anterior,
                   AVG(receita) OVER (ORDER BY data ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS media_7,
                   RANK() OVER (ORDER BY receita DESC) AS rank_receita
            FROM serie ORDER BY data
        """, conn)
    payload = {"linhas": int(len(out)), "amostra": out.head(8).to_dict(orient="records")}
    csv_path = destination.with_name("features_janela.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(csv_path, index=False)
    return dump_json(destination, payload)
