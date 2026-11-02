"""Motor do projeto 091 — Versionamento de modelo."""

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

from sklearn.linear_model import LogisticRegression
import hashlib, pickle

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    y = frame["alvo"]
    x = frame.drop(columns=["alvo"])
    model = LogisticRegression(max_iter=300).fit(x, y)
    blob = pickle.dumps(model)
    digest = hashlib.sha256(blob).hexdigest()
    art = destination.with_name("model.pkl")
    art.parent.mkdir(parents=True, exist_ok=True)
    art.write_bytes(blob)
    registro = {"versao": "v1", "sha256": digest, "n": int(len(frame)), "features": list(x.columns), "artefato": str(art)}
    return dump_json(destination, registro)
