"""Motor do projeto 047 — Encoding categórico."""

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

from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder

def run(source: Path, destination: Path) -> dict[str, Any]:
    frame = pd.read_csv(source)
    cats = frame[["uf", "canal"]]
    onehot = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    ordinal = OrdinalEncoder()
    oh = onehot.fit_transform(cats)
    ord_ = ordinal.fit_transform(cats)
    payload = {
        "n": int(len(frame)),
        "onehot_dim": int(oh.shape[1]),
        "ordinal_dim": int(ord_.shape[1]),
        "categorias_uf": list(map(str, ordinal.categories_[0])),
    }
    out = pd.concat([frame.reset_index(drop=True), pd.DataFrame(oh, columns=onehot.get_feature_names_out())], axis=1)
    csv_path = destination.with_name("encoded.csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(csv_path, index=False)
    payload["arquivo"] = str(csv_path)
    return dump_json(destination, payload)
