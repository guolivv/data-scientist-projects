"""Motor do projeto 014 — Tabelas de frequência."""

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
    col = "uf" if "uf" in frame.columns else frame.select_dtypes(exclude=["number"]).columns[0]
    counts = frame[col].value_counts(dropna=False).rename_axis(col).reset_index(name="n")
    counts["pct"] = (counts["n"] / counts["n"].sum()).round(4)
    counts["acumulado"] = counts["pct"].cumsum().round(4)
    csv_path = destination.with_name("frequencias.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    counts.to_csv(csv_path, index=False)
    payload = {"coluna": str(col), "n_niveis": int(len(counts)), "top": counts.head(5).to_dict(orient="records")}
    return dump_json(destination, payload)
