"""Motor do projeto 001 — Leitura tabular com pandas."""

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
    payload = {
        "linhas": int(len(frame)),
        "colunas": list(map(str, frame.columns)),
        "n_colunas": int(frame.shape[1]),
        "tipos": {str(col): str(dtype) for col, dtype in frame.dtypes.items()},
        "nulos": {str(col): int(frame[col].isna().sum()) for col in frame.columns},
    }
    return dump_json(destination, payload)
