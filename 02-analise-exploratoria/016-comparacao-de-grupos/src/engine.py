"""Motor do projeto 016 — Comparação de grupos."""

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
    grouped = frame.groupby("canal")["converteu"].agg(["count", "mean", "sum"]).reset_index()
    grouped["taxa"] = grouped["mean"].round(4)
    grouped["se"] = np.sqrt(grouped["taxa"] * (1 - grouped["taxa"]) / grouped["count"])
    grouped["ic_low"] = (grouped["taxa"] - 1.96 * grouped["se"]).clip(0, 1).round(4)
    grouped["ic_high"] = (grouped["taxa"] + 1.96 * grouped["se"]).clip(0, 1).round(4)
    payload = {"grupos": grouped[["canal", "count", "taxa", "ic_low", "ic_high"]].to_dict(orient="records")}
    return dump_json(destination, payload)
