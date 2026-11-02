"""Motor do projeto 049 — Binning e discretização."""

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

from sklearn.preprocessing import KBinsDiscretizer

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    x = frame[["idade"]]
    uniforme = KBinsDiscretizer(n_bins=4, encode="ordinal", strategy="uniform")
    quantil = KBinsDiscretizer(n_bins=4, encode="ordinal", strategy="quantile")
    payload = {
        "uniforme": uniforme.fit_transform(x).ravel().tolist()[:12],
        "quantil": quantil.fit_transform(x).ravel().tolist()[:12],
        "bordas_uniforme": uniforme.bin_edges_[0].tolist(),
        "bordas_quantil": quantil.bin_edges_[0].tolist(),
    }
    return dump_json(destination, payload)
