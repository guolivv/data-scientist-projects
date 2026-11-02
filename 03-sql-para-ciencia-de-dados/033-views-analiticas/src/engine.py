"""Motor do projeto 033 — Views analíticas locais."""

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
    pedidos = pd.read_csv(source)
    itens = pd.read_csv(source.with_name("itens.csv"))
    db = destination.parent / "analitico.sqlite"
    db.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db) as conn:
        pedidos.to_sql("pedidos", conn, index=False, if_exists="replace")
        itens.to_sql("itens", conn, index=False, if_exists="replace")
        conn.execute("""
            CREATE VIEW IF NOT EXISTS vw_pedido_item AS
            SELECT p.pedido_id, p.data, p.cliente_id, i.sku, i.quantidade, i.preco,
                   i.quantidade * i.preco AS receita
            FROM pedidos p JOIN itens i ON i.pedido_id = p.pedido_id
        """)
        resumo = pd.read_sql("SELECT COUNT(*) AS linhas, ROUND(SUM(receita),2) AS receita FROM vw_pedido_item", conn)
    payload = {"sqlite": str(db), "view": "vw_pedido_item", "resumo": resumo.to_dict(orient="records")[0]}
    return dump_json(destination, payload)
