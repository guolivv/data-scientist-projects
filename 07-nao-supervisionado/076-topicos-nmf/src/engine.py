"""Motor do projeto 076 — Tópicos com NMF."""

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

from sklearn.decomposition import NMF
from sklearn.feature_extraction.text import TfidfVectorizer

def run(source: Path, destination: Path) -> dict[str, Any]:
    textos = pd.read_csv(source)["texto"].astype(str)
    vec = TfidfVectorizer(max_features=80)
    x = vec.fit_transform(textos)
    model = NMF(n_components=3, random_state=42, max_iter=400)
    model.fit(x)
    vocab = np.array(vec.get_feature_names_out())
    topicos = []
    for i, row in enumerate(model.components_):
        topicos.append({"topico": i, "termos": vocab[row.argsort()[-6:][::-1]].tolist()})
    payload = {"topicos": topicos, "n_documentos": int(len(textos))}
    return dump_json(destination, payload)
