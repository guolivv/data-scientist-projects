"""Motor do projeto 038 — Teste qui-quadrado."""

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
    tab = pd.crosstab(frame["dispositivo"], frame["converteu"])
    expected = pd.DataFrame(np.outer(tab.sum(axis=1), tab.sum(axis=0)) / tab.values.sum(), index=tab.index, columns=tab.columns)
    chi = float(((tab - expected) ** 2 / expected.replace(0, np.nan)).sum().sum())
    df = (tab.shape[0] - 1) * (tab.shape[1] - 1)
    payload = {"tabela": tab.to_dict(), "chi2": chi, "df": int(df)}
    return dump_json(destination, payload)
