"""Motor do projeto 048 — Scaling e normalização."""

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

from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    cols = [c for c in ("renda", "idade") if c in frame.columns]
    x = frame[cols]
    resumo = {}
    for name, scaler in (("standard", StandardScaler()), ("minmax", MinMaxScaler()), ("robust", RobustScaler())):
        z = scaler.fit_transform(x)
        resumo[name] = {"min": z.min(axis=0).tolist(), "max": z.max(axis=0).tolist(), "media": z.mean(axis=0).tolist()}
    payload = {"colunas": cols, "scalers": resumo}
    return dump_json(destination, payload)
