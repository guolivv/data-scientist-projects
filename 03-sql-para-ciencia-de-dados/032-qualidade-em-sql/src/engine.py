"""Motor do projeto 032 — Testes de qualidade em SQL."""

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
        frame.to_sql("mart", conn, index=False, if_exists="replace")
        nulos = conn.execute("SELECT COUNT(*) FROM mart WHERE pedido_id IS NULL OR receita IS NULL").fetchone()[0]
        dup = conn.execute("SELECT COUNT(*) FROM (SELECT pedido_id FROM mart GROUP BY pedido_id HAVING COUNT(*)>1)").fetchone()[0]
        faixa = conn.execute("SELECT COUNT(*) FROM mart WHERE receita < 0").fetchone()[0]
    falhas = []
    if nulos:
        falhas.append("not_null")
    if dup:
        falhas.append("unique")
    if faixa:
        falhas.append("faixa")
    payload = {"nulos": int(nulos), "duplicatas": int(dup), "receita_negativa": int(faixa), "falhas": falhas, "passou": not falhas}
    return dump_json(destination, payload)
