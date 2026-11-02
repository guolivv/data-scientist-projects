"""Motor do projeto 083 — TF-IDF e similaridade."""

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

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def run(source: Path, destination: Path) -> dict[str, Any]:
    textos = pd.read_csv(source)["texto"].astype(str)
    x = TfidfVectorizer(max_features=80).fit_transform(textos)
    sim = cosine_similarity(x)
    np.fill_diagonal(sim, 0)
    i, j = np.unravel_index(sim.argmax(), sim.shape)
    payload = {"par_mais_similar": [int(i), int(j)], "similaridade": float(sim[i, j]), "n": int(len(textos))}
    return dump_json(destination, payload)
