"""Motor do projeto 006 — Junção de tabelas."""

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
    pedidos = pd.read_csv(source)
    clientes = pd.read_csv(source.with_name("clientes.csv"))
    merged = pedidos.merge(clientes, on="cliente_id", how="left")
    orfaos = merged[merged["segmento"].isna()] if "segmento" in merged.columns else merged[merged["cliente_id"].isna()]
    payload = {
        "pedidos": int(len(pedidos)),
        "clientes": int(len(clientes)),
        "unificados": int(len(merged)),
        "orfaos": int(len(orfaos)),
        "match_rate": round(1 - len(orfaos) / max(len(pedidos), 1), 4),
    }
    csv_path = destination.with_name("base_unificada.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(csv_path, index=False)
    payload["arquivo"] = str(csv_path)
    return dump_json(destination, payload)
