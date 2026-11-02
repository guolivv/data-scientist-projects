"""Motor do projeto 082 — Bag of words."""

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

from sklearn.feature_extraction.text import CountVectorizer

def run(source: Path, destination: Path) -> dict[str, Any]:
    textos = pd.read_csv(source)["texto"].astype(str)
    vec = CountVectorizer(max_features=50)
    x = vec.fit_transform(textos)
    freq = np.asarray(x.sum(axis=0)).ravel()
    vocab = vec.get_feature_names_out()
    top = sorted(zip(vocab, freq), key=lambda t: -t[1])[:10]
    payload = {"n_documentos": int(x.shape[0]), "n_termos": int(x.shape[1]), "top_termos": [{"termo": t, "n": int(c)} for t, c in top]}
    return dump_json(destination, payload)
