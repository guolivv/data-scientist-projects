"""Motor do projeto 034 — Dicionário analítico."""

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
    regras = {
        "pedido_id": "identificador do pedido",
        "data": "data do pedido (AAAA-MM-DD)",
        "receita": "valor em reais",
        "cliente_id": "chave do cliente",
        "categoria": "categoria mercadológica",
    }
    linhas = ["# Dicionário analítico", ""]
    registros = []
    for col in frame.columns:
        dtype = str(frame[col].dtype)
        registros.append({
            "coluna": col,
            "tipo": dtype,
            "nulos": int(frame[col].isna().sum()),
            "nunique": int(frame[col].nunique()),
            "descricao": regras.get(col, "sem descrição cadastrada"),
        })
        linhas.append(f"- `{col}` ({dtype}): {regras.get(col, 'sem descrição cadastrada')}")
    md = destination.with_suffix(".md")
    md.parent.mkdir(parents=True, exist_ok=True)
    md.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    payload = {"colunas": registros, "markdown": str(md)}
    return dump_json(destination, payload)
