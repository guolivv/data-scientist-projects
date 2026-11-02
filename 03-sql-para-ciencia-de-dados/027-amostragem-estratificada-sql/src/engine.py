"""Motor do projeto 027 — Amostragem estratificada em SQL."""

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
    fracao = 0.2
    partes = []
    for uf, grupo in frame.groupby("uf"):
        n = max(1, int(round(len(grupo) * fracao)))
        partes.append(grupo.sample(n=min(n, len(grupo)), random_state=42))
    amostra = pd.concat(partes, ignore_index=True)
    pop = frame["uf"].value_counts(normalize=True).round(3).to_dict()
    amp = amostra["uf"].value_counts(normalize=True).round(3).to_dict()
    payload = {"n_pop": int(len(frame)), "n_amostra": int(len(amostra)), "mix_pop": pop, "mix_amostra": amp}
    return dump_json(destination, payload)
