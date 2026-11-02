"""Motor do projeto 029 — Join e vazamento temporal."""

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
    eventos = pd.read_csv(source, parse_dates=["evento_em"])
    cadastro = pd.read_csv(source.with_name("cadastro.csv"), parse_dates=["vigente_em"])
    leak = eventos.merge(cadastro, on="cliente_id", how="left")
    leak_futuro = leak[leak["vigente_em"] > leak["evento_em"]]
    cadastro = cadastro.sort_values("vigente_em")
    eventos = eventos.sort_values("evento_em")
    asof = pd.merge_asof(
        eventos.sort_values("evento_em"),
        cadastro.sort_values("vigente_em"),
        by="cliente_id",
        left_on="evento_em",
        right_on="vigente_em",
        direction="backward",
    )
    payload = {
        "eventos": int(len(eventos)),
        "joins_com_futuro": int(len(leak_futuro)),
        "asof_linhas": int(len(asof)),
        "asof_sem_cadastro": int(asof["segmento"].isna().sum()) if "segmento" in asof.columns else 0,
    }
    return dump_json(destination, payload)
