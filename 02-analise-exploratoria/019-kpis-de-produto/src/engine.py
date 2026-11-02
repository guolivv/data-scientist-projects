"""Motor do projeto 019 — KPIs de produto."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def dump_json(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return payload

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    visitantes = int(frame["visitante_id"].nunique())
    compradores = int(frame.loc[frame["comprou"] == 1, "visitante_id"].nunique())
    conversao = compradores / max(visitantes, 1)
    ticket = float(frame.loc[frame["comprou"] == 1, "receita"].mean()) if compradores else 0.0
    d7 = float(frame["retido_d7"].mean()) if "retido_d7" in frame.columns else None
    payload = {
        "visitantes": visitantes,
        "compradores": compradores,
        "conversao": round(conversao, 4),
        "ticket": round(ticket, 2),
        "retencao_d7": None if d7 is None else round(d7, 4),
        "definicoes": {
            "conversao": "compradores únicos / visitantes únicos",
            "ticket": "média de receita entre quem comprou",
            "retencao_d7": "média da flag retido_d7",
        },
    }
    return dump_json(destination, payload)
