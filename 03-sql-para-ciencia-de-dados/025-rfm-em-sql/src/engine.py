"""Motor do projeto 025 — RFM em SQL."""

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
    frame = pd.read_csv(source, parse_dates=["data"])
    snapshot = frame["data"].max() + pd.Timedelta(days=1)
    rfm = frame.groupby("cliente_id").agg(
        recencia=("data", lambda s: (snapshot - s.max()).days),
        frequencia=("pedido_id", "nunique"),
        valor=("receita", "sum"),
    ).reset_index()
    rfm["r"] = pd.qcut(rfm["recencia"].rank(method="first"), 4, labels=[4, 3, 2, 1]).astype(int)
    rfm["f"] = pd.qcut(rfm["frequencia"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
    rfm["m"] = pd.qcut(rfm["valor"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
    rfm["rfm"] = rfm["r"].astype(str) + rfm["f"].astype(str) + rfm["m"].astype(str)
    payload = {"n_clientes": int(len(rfm)), "score_medio": rfm[["r", "f", "m"]].mean().round(2).to_dict(), "top": rfm.sort_values("valor", ascending=False).head(5).to_dict(orient="records")}
    csv_path = destination.with_name("rfm.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    rfm.to_csv(csv_path, index=False)
    payload["arquivo"] = str(csv_path)
    return dump_json(destination, payload)
