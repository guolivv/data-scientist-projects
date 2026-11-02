"""Motor do projeto 021 — Carga de CSV no SQLite."""

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
    db = destination.parent / "vendas.sqlite"
    db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db) as conn:
        frame.to_sql("vendas", conn, index=False, if_exists="replace")
        conn.execute("CREATE INDEX IF NOT EXISTS ix_vendas_data ON vendas(data)")
        receita = conn.execute("SELECT ROUND(SUM(receita),2) FROM vendas").fetchone()[0]
        n = conn.execute("SELECT COUNT(*) FROM vendas").fetchone()[0]
    payload = {"linhas": int(n), "receita": float(receita or 0), "sqlite": str(db)}
    return dump_json(destination, payload)
