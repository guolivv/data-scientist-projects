"""Motor do projeto 050 — Features de calendário."""

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

FERIADOS = {"01-01", "04-21", "09-07", "12-25"}

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source, parse_dates=["data"])
    frame["mes"] = frame["data"].dt.month
    frame["dow"] = frame["data"].dt.dayofweek
    frame["fim_de_mes"] = (frame["data"] + pd.Timedelta(days=1)).dt.month.ne(frame["mes"]).astype(int)
    frame["feriado"] = frame["data"].dt.strftime("%m-%d").isin(FERIADOS).astype(int)
    csv_path = destination.with_name("calendar_features.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(csv_path, index=False)
    payload = {"linhas": int(len(frame)), "n_feriados": int(frame["feriado"].sum()), "arquivo": str(csv_path)}
    return dump_json(destination, payload)
