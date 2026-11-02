"""Motor do projeto 092 — Monitoramento de predição."""

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
    frame = pd.read_csv(source, parse_dates=["data"])
    daily = frame.groupby("data")["score"].agg(["mean", "std", "count"]).reset_index()
    baseline = float(daily["mean"].iloc[:7].mean())
    daily["alerta"] = (daily["mean"] < baseline - 0.08).astype(int)
    daily["data"] = daily["data"].astype(str)
    payload = {"baseline": baseline, "dias_alerta": int(daily["alerta"].sum()), "serie": daily.tail(10).to_dict(orient="records")}
    return dump_json(destination, payload)
