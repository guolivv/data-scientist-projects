"""Motor do projeto 088 — Fairness e disparidade."""

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
    frame = pd.read_csv(source)
    taxas = frame.groupby("grupo")["aprovado"].mean().to_dict()
    vals = list(taxas.values())
    razao = min(vals) / max(vals) if max(vals) else None
    payload = {"taxas": {str(k): float(v) for k, v in taxas.items()}, "razao_disparidade": razao, "limiar_80": razao is not None and razao >= 0.8}
    return dump_json(destination, payload)
