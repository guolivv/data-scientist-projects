"""Motor do projeto 028 — Pivot e unpivot."""

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
    largo = pd.read_csv(source)
    id_vars = [c for c in largo.columns if c in {"sku", "categoria"}]
    value_vars = [c for c in largo.columns if c not in id_vars]
    longo = largo.melt(id_vars=id_vars, value_vars=value_vars, var_name="mes", value_name="receita")
    payload = {"colunas_largas": value_vars, "linhas_longas": int(len(longo)), "formato": "tidy"}
    csv_path = destination.with_name("longo.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    longo.to_csv(csv_path, index=False)
    payload["arquivo"] = str(csv_path)
    return dump_json(destination, payload)
