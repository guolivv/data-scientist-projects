"""Motor do projeto 051 — Target encoding com CV."""

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

from sklearn.model_selection import KFold

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    fold = KFold(n_splits=5, shuffle=True, random_state=42)
    encoded = np.zeros(len(frame))
    global_mean = float(frame["alvo"].mean())
    for train_idx, val_idx in fold.split(frame):
        means = frame.iloc[train_idx].groupby("cidade")["alvo"].mean()
        encoded[val_idx] = frame.iloc[val_idx]["cidade"].map(means).fillna(global_mean)
    naive = frame["cidade"].map(frame.groupby("cidade")["alvo"].mean())
    payload = {
        "media_global": global_mean,
        "corr_cv": float(pd.Series(encoded).corr(frame["alvo"])),
        "corr_ingenuo": float(naive.corr(frame["alvo"])),
        "leakage_reduzido": True,
    }
    return dump_json(destination, payload)
